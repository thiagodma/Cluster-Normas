import pandas as pd
import numpy as np
import os
import re
from docx import Document

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

    def import_data(self):

        path = 'Arquivos_DOCX_atual_31_julho_2019/'
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

        for unique_macrotema in unique_macrotemas:
            if not os.path.isdir(unique_macrotema): os.mkdir(unique_macrotema)
            os.chdir(unique_macrotema)
            for i in range(len(self.textos)):
                if self.macrotemas[i] == unique_macrotema:
                    fo = open(self.nomes_normas[i][:-5]  + '.txt', 'w+')
                    fo.writelines(self.textos[i])
                    fo.close()
            os.chdir('..')
        os.chdir('..')
        data_csv = pd.DataFrame(list(zip(self.nomes_normas,self.macrotemas,self.ementas,self.textos)),
        columns=['nomes_normas','macrotemas','ementas','textos'])
        data_csv.to_csv('Data.csv',sep='|',index=False,encoding='utf-8')
