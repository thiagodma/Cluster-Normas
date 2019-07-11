#Importando os pacotes que seraoo utilizados
from stop_words import get_stop_words
from docx import Document
import os, os.path, glob, re, unicodedata, time, nltk
from sklearn.decomposition import TruncatedSVD
from sklearn.decomposition import LatentDirichletAllocation
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
nltk.download('rslp')
nltk.download('stopwords')
#==============================================================================


#Definindo algumas variaveis que serao uteis
#Dicionario para normalizacao dos nomes de arquivos
tipos_norma = {'PRT':'Portaria', 'RDC':'RDC', 'RES':'RE', 'RE':'RE', 
               'IN':'IN', 'INC':'INC', 'PRTC':'PRTC'}

# stop-words provisorio
stop_words = get_stop_words('portuguese') + ['','art','dou','secao','pag','pagina', 'in', 'inc', ]

# Aprimorar romanos
#romanos_t0 = [' i ','ii','iii',' iv ',' v ',' vi ','vii','viii',' ix ',' x ',
#           ' xi ','xii','xiii']

base_romanos = ['i','v','x','l','c']


#==============================================================================


#Definindo as funcoes da biblioteca

# Recodificacao em utf8, removendo cedilhas acentos e coisas de latin
def limpa_utf8(palavra):    

    # Unicode normalize transforma um caracter em seu equivalente em latin.
    nfkd = unicodedata.normalize('NFKD', palavra)
    palavraSemAcento = u"".join([c for c in nfkd if not unicodedata.combining(c)])

    # Usa expressao regular para retornar a palavra apenas com numeros, letras e espaco
    #return re.sub('[^a-zA-Z/ \\\]', '', palavraSemAcento)
    palavraSemHifen = re.sub('[-\/]', ' ', palavraSemAcento)
    return re.sub('[^a-zA-Z ]', '', palavraSemHifen)


# Funcao de remocao de algarismos Romanos
def romanos_lento(palavra_original):
    palavra = limpa_utf8(palavra_original)
    
    # Nada que tenha um so caracter interessa
    if len(palavra) < 2: return ''
    # Se for grande, dificilmente sera um romano
    if len(palavra) > 5: return palavra
    
    # Vamos testar agora se eh um algasrismo romano
    for letra in palavra:
        if letra not in base_romanos:
            # Se alguma letra nao for romano da base de romanos, entao retorna
            return palavra

    # Se nao retornou antes, entao as poucas letras estao todas no grupo de romanos, vamos descartar
    return ''


def roman2num(roman, values={'m': 1000, 'd': 500, 'c': 100, 'l': 50, 
                                'x': 10, 'v': 5, 'i': 1}):
    
    if (roman == ''): return ''
    out = re.sub('[^mdclxvi]', '', roman)
    if (len(out) != len(roman)):
        return roman
   
    numbers = []
    for char in roman:
        numbers.append(values[char]) 
    total = 0
    if(len(numbers) > 1):
        for num1, num2 in zip(numbers, numbers[1:]):
            if num1 >= num2:
                total += num1
            else:
                total -= num1
        return str(total + num2)
    else:
        return str(numbers[0])

# Tratamento principal: prepara o texto para contagem
def trata_textos(texto_limpo):
    # Remove digitos
    texto_limpo = re.sub("\d", " ", texto_limpo)
    
    #Remove hifens e barras
    texto_limpo = re.sub('[-\/]', ' ', texto_limpo)
    
    #Remove espaços extras
    texto_limpo = re.sub(' +', ' ', texto_limpo)
    
    # Minuscula
    texto_limpo = texto_limpo.lower()
    
    # Remove pontuacaoo e quebras de linha
    #texto_limpo = re.sub('[\n\r]', '', texto_limpo)
    #texto_limpo = re.sub(r'([^\s\w]|_)+', '', texto_limpo)
        
    # So a partir daqui o texto vira lista mesmo    
    texto_limpo = texto_limpo.split(' ')
    
    # Vamos atacar os romanos
    texto_limpo = [romanos_lento(w) for w in texto_limpo]
    
    #tira stop-words
    texto_limpo = [w for w in texto_limpo if w not in stop_words]
    
    # retorna o texto simplificado
    texto_limpo = ' '.join(texto_limpo)
    
    #Remove espaços extras
    texto_limpo = re.sub(' +', ' ', texto_limpo)
    
    # Tratamento meio boca para i ii iii
    texto_limpo = re.sub('i+','i', texto_limpo)
    
    return texto_limpo


# Esta funcao serve para transformar o nome do arquivo em um formato 
# Tipo_norma numero_norma/AAAA (sem separadores de milhar)
def normaliza_nome_arquivo(nome_arq):
    # Este eh o dicionario para normalizar os nomes de normas
    global tipos_norma
    n_tratado = nome_arq
    # Procura o ultimo digito do nome do arquivo
    acha_digitos = re.match('.+([0-9])[^0-9]*$', nome_arq)
    # Posicao do ultimo digito encontrada
    pos_ultimo_digito = acha_digitos.start(1)
    # Corta o resto alem do ultimo di­gito
    nome_arq = nome_arq[:pos_ultimo_digito + 1]
    # Separa no split por underline
    nome_arq = nome_arq.split('_')
    # Parada de emergencia para nome de arquivos fora do padrao 
    if len(nome_arq) < 3:
        raise ValueError('Nome de arquivo fora de padrao:', n_tratado)
    # Monta nome_arq em norma_citadora no padrao desejado tipo_norma numero_norma/AAAA
    # JÃ¡ Ã© aplicado tambem o dicionario tipos_norma ao nome_arq[0], normalizando
    # assim o tipo da norma
    numeracao = nome_arq[-2].strip()
    # Adicionando o '0' Ã s normas que sao numeral unico, como IN 1/2014
    if len(numeracao) == 1: numeracao = '0' + numeracao     
    norma_citadora = tipos_norma[nome_arq[0].strip()] + ' ' + numeracao + '/' + nome_arq[-1]
    # Retorna nome_arq normalizado
    return norma_citadora 


# Importa arquivos. Esse codigo deve funcionar em qualquer computador em que a pasta 'Arquivos DOCX - atual - fevereiro.2019'
# esteja no diretório de trabalho
def importa_normas():
    #path ='Z:\\GGREG_GERAL\\#GECOR\\Inteligencia Regulatoria\\Normativo Compilado Anvisa - Painel\\Arquivos DOCX - atual - fevereiro.2019'
    path = 'Arquivos DOCX - atual - fevereiro.2019'
    #path ='C:\\Users\\paulo.gferreira\\Desktop\\Python\\Normas\\Normativos2'
    os.chdir(path)
    
    # Lista de pastas no diretorio atual
    pastas = [name for name in os.listdir('.')]
    
    arquivos = []
    resolucoes = []
    nome_arquivos = []
    
    for i in range(0,len(pastas)):
        # Faz o diretorio mudar para a pasta de cada ano
        os.chdir(pastas[i])
        # Pega todos os arquivos da pasta
        arquivos = glob.glob('*.docx')
        print('A pasta ' + str(i) + ' tem ' + str(len(arquivos)) + ' arquivos')
        t = time.time()
        for w in range(0, len(arquivos)):
            doc = Document(arquivos[w])
            doc.paragraphs
            texto = [parag.text for parag in doc.paragraphs]
            texto = '\n'.join(texto)
            # Substituicoes para desonerar o vetor Start, legado
            resolucoes.append(trata_textos(texto))
            nome_arquivos.append(normaliza_nome_arquivo(arquivos[w]))
            
        elapsed = time.time() - t
        print('Tempo para importar a pasta ' + str(i) + ': ' + str(elapsed) + '\n')
        os.chdir('..')
    #volta para o diretorio inicial
    os.chdir('..')
    return resolucoes, nome_arquivos


#Faz os stemming nas palavras utilizando o pacote NLTK com o RSLP Portuguese stemmer
def stem(resolucoes):
    
    #nltk.download('rslp') so precisa usar isso na primeira da vida que roda o stemming no PC
    print('Comecou a fazer o stemming.\n')
    t = time.time()
    #Inicializo a lista que será o retorno da funcao
    res = []
    
    #inicializando o objeto stemmer
    stemmer = nltk.stem.RSLPStemmer()
    
    for resolucao in resolucoes:
        #Faz o stemming para cada palavra na resolucao
        palavras_stemmed_resolucao = [stemmer.stem(word) for word in resolucao.split()]
        #Faz o append da resolucao que passou pelo stemming
        res.append(" ".join(palavras_stemmed_resolucao))
    
    print('Tempo para fazer o stemming: ' + str(time.time() - t) + 's \n')
        
    return res

#Visualiza as cluster definidas pelo algoritmo. Além disso também retorna o número
#de normas por cluster
def analisa_clusters(base_tfidf, id_clusters):
    
    clusters = np.unique(id_clusters)
    
    #inicializa o output da funcao
    n_normas = np.zeros(len(clusters)) #numero de normas pertencentes a uma cluster
    
    #reduz a dimensionalidade para 2 dimensoes
    base_tfidf_reduced = SVD(2,base_tfidf)
    X = base_tfidf_reduced[:,0]
    Y = base_tfidf_reduced[:,1]
    
    colors = cm.rainbow(np.linspace(0, 1, len(n_normas)))

    for cluster, color in zip(clusters, colors):
        idxs = np.where(id_clusters == cluster) #a primeira cluster não é a 0 e sim a 1
        n_normas[cluster-1] = len(idxs[0])
        x = X[idxs[0]]
        y = Y[idxs[0]]
        plt.scatter(x, y, color=color)
    
    return n_normas 
        
#Reduz a dimensionalidade dos dados
def SVD(dim,base_tfidf):
    svd = TruncatedSVD(n_components=dim)
    base_tfidf_reduced = svd.fit_transform(base_tfidf)
    print('Número de dimensoes de entrada: ' + str(base_tfidf.shape[1]))
    print(str(dim) + ' dimensões explicam ' + str(svd.explained_variance_ratio_.sum()) + ' da variância.\n' )
    return base_tfidf_reduced

#Cria um objeto da classe LatentDirichletAllocation
def build_lda(base_tfidf_reduced, num_of_topics=10):
    lda = LatentDirichletAllocation(n_components=num_of_topics,
                                    max_iter=15,
                                    learning_method='online',
                                    random_state=0)
    lda.fit(base_tfidf_reduced + 1)
    return lda

def display_word_distribution(model,n_word, feature_names):
    for topic_idx, topic in enumerate(model.components_):
        print("Topic %d:" % (topic_idx))
        words = []
        for i in topic.argsort()[:-n_word - 1:-1]:
            words.append(feature_names[i])
        print(words)



#==============================================================================