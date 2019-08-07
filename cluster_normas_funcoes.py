#Importando os pacotes que seraoo utilizados
from stop_words import get_stop_words
from docx import Document
import os, os.path, glob, re, unicodedata, time, nltk
from sklearn.decomposition import TruncatedSVD
from wordcloud import WordCloud
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import pdb
#nltk.download('rslp')
#nltk.download('stopwords')
#==============================================================================

#Definindo algumas variaveis que serao uteis
#Dicionario para normalizacao dos nomes de arquivos
tipos_norma = {'PRT':'Portaria', 'RDC':'RDC', 'RES':'RE', 'RE':'RE',
               'IN':'IN', 'INC':'INC', 'PRTC':'PRTC'}

#==============================================================================


def define_stop_words():
    '''
    Pega stopwords de diferentes bibliotecas e as trata para ficarem no formato correto
    '''

    stop_words = get_stop_words('portuguese')
    stop_words = stop_words + nltk.corpus.stopwords.words('portuguese')
    stop_words = stop_words + ['art','dou','secao','pag','pagina', 'in', 'inc', 'obs', 'sob', 'ltda','ia']
    stop_words = stop_words + ['ndash', 'mdash', 'lsquo','rsquo','ldquo','rdquo','bull','hellip','prime','lsaquo','rsaquo','frasl', 'ordm']
    stop_words = stop_words + ['prezado', 'prezados', 'prezada', 'prezadas', 'gereg', 'ggali','usuario', 'usuaria', 'deseja','gostaria', 'boa tarde', 'bom dia', 'boa noite']
    stop_words = stop_words + ['rdc','resolucao','portaria','lei','janeiro','fevereiro','marco','abril','maio','junho','julho','agosto','setembro','outubro','novembro','dezembro']
    stop_words = stop_words + ['decreto','anvisa','anvs','diretoria','colegiada','capitulo','item','regulamento','tecnico','nr','instrucao','normativa','anexo']
    stop_words = stop_words + ['paragrafo', 'unico','devem','caso','boas','vigilancia','sanitaria','cada']
    stop_words = list(dict.fromkeys(stop_words))
    stop_words = ' '.join(stop_words)
    #As stop_words vem com acentos/cedilhas. Aqui eu tiro os caracteres indesejados
    stop_words = limpa_utf8(stop_words)
    return stop_words


def limpa_utf8(texto):
    '''
    Recodifica em utf-8. Remove cedilhas, acentos e coisas de latin
    '''

    texto = texto.split()
    texto_tratado = []
    for palavra in texto:
        # Unicode normalize transforma um caracter em seu equivalente em latin.
        nfkd = unicodedata.normalize('NFKD', palavra)
        palavra_sem_acento = u"".join([c for c in nfkd if not unicodedata.combining(c)])
        texto_tratado.append(palavra_sem_acento)

    return ' '.join(texto_tratado)



def roman2num(roman, stop_words, values={'m': 1000, 'd': 500, 'c': 100, 'l': 50,
                                'x': 10, 'v': 5, 'i': 1}):
    '''
    Converte números romanos em decimais e remove stopwords.
    '''
    roman = limpa_utf8(roman)

    #remove stopwords
    if roman in stop_words:
        return ''

    #como eu vou tirar numeros de qualquer forma, posso simplesmente retornar um numero
    if(len(roman) < 2 ):
        return str(1)

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


def trata_textos(texto, stop_words):
    '''
    Trata os textos. Remove stopwords, sites, pontuacao, caracteres especiais etc. texto:str, stop_words:str
    '''

    #converte todos caracteres para letra minúscula
    texto_lower = texto.lower()
    texto_lower = re.sub(r'\xa0',' ',texto_lower)

    #encontra a seção de artigos
    artigos = re.findall(r'\n *art. *\d',texto_lower)

    if len(artigos) >=2:
        #Pega apenas o texto entre o primeiro artigo e o último
        regex = r'('+artigos[0]+')(.*)('+artigos[-1]+')'
        regex = re.sub(r'\n',r'\\n',regex)
        m = re.search(regex, texto_lower, re.DOTALL)
        texto_so_artigos = m.group(2)
    else:
        return 'norma fora de padrão'

    #tira sites
    texto_sem_sites =  re.sub('(http|www)[^ ]+','',texto_so_artigos)

    #Remove acentos e pontuação
    texto_sem_acento_pontuacao = limpa_utf8(texto_sem_sites)

    #Remove hifens e barras
    texto_sem_hifens_e_barras = re.sub('[-\/]', ' ', texto_sem_acento_pontuacao)

    #Troca qualquer tipo de espacamento por espaço
    texto_sem_espacamentos = re.sub(r'\s', ' ', texto_sem_hifens_e_barras)

    #Remove pontuacao e digitos
    texto_limpo = re.sub('[^A-Za-z]', ' ' , texto_sem_espacamentos)

    #Retira numeros romanos e stopwords
    texto_limpo = texto_limpo.split()
    texto_sem_stopwords = [roman2num(palavra,stop_words) for palavra in texto_limpo]
    texto_sem_stopwords = ' '.join(texto_sem_stopwords)

    #Remove pontuacao e digitos
    texto_limpo = re.sub('[^A-Za-z]', ' ' , texto_sem_stopwords)

    #Remove espaços extras
    texto_limpo = re.sub(' +', ' ', texto_limpo)

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
    norma_citadora = tipos_norma[nome_arq[0].strip()] + ' ' + numeracao + '_' + nome_arq[-1]
    # Retorna nome_arq normalizado
    return norma_citadora


def importa_normas(stop_words):
    '''
    Importa arquivos. Esse código deve funcionar em qualquer computador em que a pasta 'Arquivos DOCX - atual - fevereiro.2019'
    esteja no diretório de trabalho
    '''

    path = 'Arquivos_DOCX_atual_31_julho_2019'
    os.chdir(path)

    # Lista de pastas no diretorio atual
    pastas = [name for name in os.listdir('.')]

    arquivos = []
    resolucoes_tratadas = []
    resolucoes = []
    nome_arquivos = []

    for i in range(0,len(pastas)):
        # Faz o diretorio mudar para a pasta de cada ano
        os.chdir(pastas[i])
        # Pega todos os arquivos da pasta
        arquivos = glob.glob('*.docx')
        print('\nA pasta ' + str(i) + ' tem ' + str(len(arquivos)) + ' arquivos')
        t = time.time()
        for w in range(0, len(arquivos)):
            if int(arquivos[w][-9:-5]) >= 1999: #pega apenas as normas de 1999 pra frente
                doc = Document(arquivos[w])
                doc.paragraphs
                texto = [parag.text for parag in doc.paragraphs]
                texto = '\n'.join(texto)
                # Substituicoes para desonerar o vetor Start, legado
                resolucoes.append(texto)
                resolucoes_tratadas.append(trata_textos(texto, stop_words))
                nome_arquivos.append(arquivos[w])

        elapsed = time.time() - t
        print('Tempo para importar a pasta ' + str(i) + ': ' + str(elapsed) + '\n')
        os.chdir('..')
    #volta para o diretorio inicial
    os.chdir('..')
    return resolucoes_tratadas, resolucoes, nome_arquivos


def stem(resolucoes):
    '''
    Faz o stemming nas palavras utilizando o pacote nltk com o RSLP Portuguese stemmer.
    '''

    print('Comecou a fazer o stemming.')
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

    print('Tempo para fazer o stemming: ' + str(time.time() - t) + '\n')

    return res

def analisa_clusters(base_tfidf, id_clusters):
    '''
    Tenta visualizar as cluster definidas. Além disso retorna o número de normas por cluster.
    '''

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

def SVD(dim,base_tfidf):
    '''
    Reduz a dimensionalidade dos dados de entrada.
    dim: número de dimensões desejada (int)
    base_tfidf: base de dados a ter sua dimensionalidade reduzida
    '''

    print('Começou a redução de dimensionalidade.')
    t = time.time()
    svd = TruncatedSVD(n_components = dim, random_state = 42)
    base_tfidf_reduced = svd.fit_transform(base_tfidf)
    print('Número de dimensoes de entrada: ' + str(base_tfidf.shape[1]))
    print(str(dim) + ' dimensões explicam ' + str(svd.explained_variance_ratio_.sum()) + ' da variância.')
    elpsd = time.time() - t
    print('Tempo para fazer a redução de dimensionalidade: ' + str(elpsd) + '\n')
    return base_tfidf_reduced


def mostra_conteudo_clusters(cluster,n_amostras,respostas,it_aux):
    '''
    Salva 'n_amostras' da cluster 'cluster' em um arquivo txt para facilitar a visualização.
    '''
    df = pd.read_csv(str(it_aux) + 'texto_respostas_por_cluster.csv', sep='|')
    a = df[df['cluster_id'] == cluster]

    if a.shape[0] >= n_amostras: mostra = a.sample(n_amostras,random_state = 42)
    else : mostra = a

    fo = open(r'conteudo_cluster'+str(cluster)+'_n_'+str(a.shape[0])+'.txt', 'w+')

    for i in range(mostra.shape[0]):
        id_resposta = mostra.iloc[i,1]
        fo.writelines('ID da Resposta: ' + str(id_resposta) + '\n')
        idx = mostra.index[mostra['resposta_id'] == id_resposta].tolist()[0]
        fo.writelines(respostas[idx])
        fo.write('\n\n')

    fo.close()


def generate_wordcloud(cluster,stop_words, resolucoes_tratadas):
    '''
    Gera uma nuvem de palavras de uma cluster 'cluster'.
    '''
    df = pd.read_csv('cluster_normas_cosseno.csv',sep='|')
    a = df[df['cluster_id'] == cluster]

    L=[]
    for i in range(a.shape[0]):
        L.append(resolucoes_tratadas[a.iloc[i,2]])

    text = '\n'.join(L)


    wordcloud = WordCloud(stopwords=stop_words.split()+['laboratorio','laboratorios','rdc']).generate(text)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()

#==============================================================================
