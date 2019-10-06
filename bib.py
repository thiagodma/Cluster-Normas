import pandas as pd
import numpy as np
import os
import re
from docx import Document
import unicodedata

class Data():

    def __init__(self):
        self.tabela = pd.read_csv('Macrotemas_python.csv',sep='|',encoding='utf-8')
        self.tabela = self.tabela.rename(columns={'Macrotema atual':'Macrotema_atual'})
        self.tabela['Macrotema_atual'] = self.tabela['Macrotema_atual'].map(str.lower)
        self.tabela['Citadora'] = self.tabela['Citadora'].map(lambda x: re.sub('/','_',x))
        self.textos = []
        self.macrotemas = []
        self.nomes_normas = []
        self.ementas = []
        self.tipos_norma = {'PRT':'Portaria', 'RDC':'RDC', 'RES':'RE', 'RE':'RE',
                       'IN':'IN', 'INC':'INC', 'PRTC':'PRTC', 'PRT_SNVS':'Portaria',
                       'PRT_SVS':'Portaria','PRT_MS':'Portaria'}

    def import_data(self):

        path = 'Normas_novas_23set (atual)/'
        aux = [None for i in range(len(self.tabela['Citadora']))]
        self.tabela['isFile'] = aux
        for i in range(len(self.tabela['Citadora'])):
            file = path + self.tabela['Citadora'].iloc[i] + '.docx'
            if not os.path.exists(file): self.tabela['isFile'].iloc[i]=False
            else:
                self.tabela['isFile'].iloc[i]=True
                doc = Document(file)
                texto = [parag.text for parag in doc.paragraphs]
                texto = '\n'.join(texto)
                self.textos.append(texto)
                self.macrotemas.append(self.tabela['Macrotema_atual'].iloc[i])
                self.nomes_normas.append(self.tabela['Citadora'].iloc[i])
                self.ementas.append(self.tabela['Assunto/Ementa'].iloc[i])

    def write_data(self):

        unique_macrotemas = list(dict.fromkeys(self.macrotemas))

        if not os.path.isdir('Data'): os.mkdir('Data')
        os.chdir('Data')
        i=0
        for unique_macrotema in unique_macrotemas:
            if not os.path.isdir(unique_macrotema): os.mkdir(unique_macrotema)
            os.chdir(unique_macrotema)
            for i in range(len(self.textos)):
                if self.macrotemas[i] == unique_macrotema:
                    fo = open(self.nomes_normas[i] + '.txt', 'w+')
                    fo.writelines(self.textos[i])
                    fo.close()
                    i+=1
            os.chdir('..')
        os.chdir('..')
        data_csv = pd.DataFrame(list(zip(self.nomes_normas,self.macrotemas,self.ementas,self.textos)),
        columns=['nomes_normas','macrotemas','ementas','textos'])
        data_csv.to_csv('Data.csv',sep='|',index=False,encoding='utf-8')
        print(i)

    def normalize_file_names(self):

        path = 'Normas_novas_23set (atual)'
        files = []
        for r, d, f in os.walk(path):
            for file in f:
                files.append(file)

        os.chdir(path)
        for filename in files:
            m = re.match(r'(\w+)_(\d+)_(\d+)',filename)
            if m is not None:
                kind = m.group(1)
                if '_' in kind: kind = kind.split('_')[0]
                kind = self.tipos_norma[kind]
                numb = m.group(2)
                if len(numb)==1: numb = '0'+numb
                year = m.group(3)
                new_filename = kind + ' ' + numb + '_' + year + '.docx'
                os.rename(filename,new_filename)
        os.chdir('..')

    def clean_text(self, text):

        #finds the articles section
        articles = re.findall(r'\n *Art. *\d',text)

        if len(articles) >=2:
            #Gets the text between the first and last articles
            regex = r'('+articles[0]+')(.*)('+articles[-1]+')'
            regex = re.sub(r'\n',r'\\n',regex)
            m = re.search(regex, text, re.DOTALL)
            text_articles = m.group(2)
        else:
            return 'norma fora de padrão'

        return 'Art 1' + text_articles

    def clean_text_v2(self, text):

        clean_text = []
        for par in text.split('\n'):
            clean_par = []
            for word in par.split():
                clean_word = unicodedata.normalize('NFKD', word)
                clean_par.append(clean_word)
            clean_text.append(' '.join(clean_par))
        clean_text = '\n'.join(clean_text)

        #finds the articles section
        #articles = re.findall(r'\n *Art. *\d',clean_text)
        '''
        if len(articles) >=2:
            #Gets the text between the first and last articles
            regex = r'('+articles[0]+')(.*)('+articles[-1]+')'
            regex = re.sub(r'\n',r'\\n',regex)
            m = re.search(regex, clean_text, re.DOTALL)
            text_articles = m.group(2)
        else:
        '''
        #m = re.search(r'(.*)',clean_text, re.DOTALL)
        without_bye = re.split('entra(rá)? em (V|v)igor na data de sua publicação',clean_text)[0]
        only_important = re.split(r'RESOLVE|resolve|Resolve',without_bye)
        if len(only_important)>1: only_important = only_important[1]
        else: only_important = only_important[0]

        #finds the articles section
        articles = re.findall(r'\n *Art. *\d',only_important)
        if len(articles)>=2:
            articles = re.sub(r'\.','\.',articles[0])
            only_important_articles = re.split(articles,only_important)[1]
        else:
            only_important_articles = only_important

        #import pdb; pdb.set_trace()
        #takes out Art. structure
        if type(only_important) is not str: import pdb; pdb.set_trace()
        without_art_tags = re.sub(r'\n(a|A)rt\.? ?\d+ ?(º|\xc2\xb0)?','\n',only_important_articles)

        #takes out '§ \dº' structure
        without_par = re.sub(r'§\s\d(º|\xc2\xb0)?\s?','',without_art_tags)

        #takes out the 'IV -' structure
        without_rom = re.sub(r'\nI{1,3}|\nIV|\nV|\nVI{1,3}|\nIX|\nX|\nXI{1,3}','',without_par)

        #takes out more items structure
        without_items = re.sub(r'(\d\.)+','',without_rom)

        #takes out more items structure
        without_items2 = re.sub(r'\n\w\)','',without_items)

        #takes out double spaces
        without_double_spaces = re.sub(r' +',r' ',without_items2)

        #takes out double line breaks
        without_double_breaks = re.sub(r'\n+','\n\n',without_double_spaces)

        #takes out the ordinal number sign
        without_ord = re.sub('°','',without_double_breaks)

        #takes out some trash that appeared
        without_trash = re.sub('\n ','\n',without_ord)

        #takes out more trash
        final = re.sub('\no ','',without_trash)

        #import pdb; pdb.set_trace()
        return final

    def get_arts(self, filename:str):

        df = pd.read_csv('Data_cluster.csv', sep='|', encoding='utf-8')
        texts = list(df['textos'])
        for i in range(df.shape[0]):
            df.iloc[i,3] = self.clean_text_v2(df.iloc[i,3])

        df.to_csv(filename,sep='|',encoding='utf-8',index=False)
