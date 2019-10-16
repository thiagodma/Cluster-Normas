#Importando os pacotes que serão utilizados
from stop_words import get_stop_words
from docx import Document
import os, os.path, glob, re, unicodedata, time, nltk
from sklearn.decomposition import TruncatedSVD
from wordcloud import WordCloud
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from scipy.cluster import hierarchy
#nltk.download('rslp')
#nltk.download('stopwords')

class ClassicClustering():
    """Essa classe contém funcionalidades básicas que são úteis para a clusterização
    de textos utilizando uma abordagem clássica."""

    def __init__(self):
        '''Este é o construtor da classe.
           Aqui você deve adicionar/remover atributos para se ajustar ao seu problema

           Variáveis de entrada:
               None

           Variáveis de saída:
               None
        '''
        self.textos = [] #atributo que contém os textos sem processamento algum
        self.textos_tratados = [] #atributo que contém os textos já processados
        self.textos_stem = [] #atributo que contém os textos tratados após passar por um stemmer
        self.textos_id = [] #atributo que contém um identificador único para cada texto
        self.stop_words = [] #atributo que contém todas as stop words que serão levadas em consideração no seu problema

    def define_stop_words(self,user_defined_stopwords:list = []):
        '''
        Inicializa o atributo "stop_words" da classe pegando stopwords de
        diferentes bibliotecas e as tratando para ficarem no formato correto.

        Você pode adicionar/remover stop words para se ajustar ao seu problema.

        Variáveis de entrada:
            user_defined_stopwords: é uma variável opcional. É uma lista de
            strings que você deseja adicionar como stopwords.

        Variáveis de saída:
            None

        Obs: Em geral não é necessário modificar esse método.
        '''

        self.stop_words = get_stop_words('portuguese')
        self.stop_words = self.stop_words + nltk.corpus.stopwords.words('portuguese')
        self.stop_words = self.stop_words + ['art','dou','secao','pag','pagina', 'in', 'inc', 'obs', 'sob', 'ltda','ia']
        self.stop_words = self.stop_words + ['ndash', 'mdash', 'lsquo','rsquo','ldquo','rdquo','bull','hellip','prime','lsaquo','rsaquo','frasl', 'ordm']
        self.stop_words = self.stop_words + user_defined_stopwords
        self.stop_words = list(dict.fromkeys(self.stop_words))
        self.stop_words = ' '.join(self.stop_words)

        #As stop_words vem com acentos/cedilhas. Aqui eu tiro os caracteres indesejados
        self.stop_words = self.limpa_utf8(self.stop_words)

    def limpa_utf8(self, texto:str):
        '''
        Recodifica em utf-8. Remove cedilhas, acentos e coisas de latin.

        Variáveis de entrada:
            texto: é uma variável do tipo string que contém um texto. Não pode
            ser uma palavra única.

        Variáveis de saída:
            texto_tratado: é uma variável do tipo string que contém um texto
            recodificado em utf-8.

        Obs: Em geral não é necessário modificar esse método.
        '''

        texto = texto.split()
        texto_tratado = []
        for palavra in texto:
            # Unicode normalize transforma um caracter em seu equivalente em latin.
            nfkd = unicodedata.normalize('NFKD', palavra)
            palavra_sem_acento = u"".join([c for c in nfkd if not unicodedata.combining(c)])
            texto_tratado.append(palavra_sem_acento)

        return ' '.join(texto_tratado)

    def trata_textos(self, texto:str):
        '''
        Trata os textos. Remove stopwords, sites, pontuacao, caracteres especiais
        etc. Você pode (deve) alterar esse método para se ajustar da melhor forma
        possível ao seu problema.

        Variáveis de entrada:
            texto: é uma string que contém o texto a ser tratado.

        Variáveis de saída:
            texto_limpo: é uma string que contém o texto já tratado.

        Obs: Em geral é interessante modificar esse método. Para casos simples
        não é necessário.
        '''

        #converte todos caracteres para letra minúscula
        texto_lower = texto.lower()
        texto_lower = re.sub(r'\xa0',' ',texto_lower)

        #tira sites
        texto_sem_sites =  re.sub('(http|www)[^ ]+','',texto_lower)

        #Remove acentos e pontuação
        texto_sem_acento_pontuacao = self.limpa_utf8(texto_sem_sites)

        #Remove hifens e barras
        texto_sem_hifens_e_barras = re.sub('[-\/]', ' ', texto_sem_acento_pontuacao)

        #Troca qualquer tipo de espacamento por espaço
        texto_sem_espacamentos = re.sub(r'\s', ' ', texto_sem_hifens_e_barras)

        #Remove pontuacao e digitos
        texto_limpo = re.sub('[^A-Za-z]', ' ' , texto_sem_espacamentos)

        #Retira numeros romanos e stopwords
        texto_limpo = texto_limpo.split()
        texto_sem_stopwords = [self.tira_stopwords_e_romanos(palavra) for palavra in texto_limpo]
        texto_sem_stopwords = ' '.join(texto_sem_stopwords)

        #Remove pontuacao e digitos
        texto_limpo = re.sub('[^A-Za-z]', ' ' , texto_sem_stopwords)

        #Remove espaços extras
        texto_limpo = re.sub(' +', ' ', texto_limpo)

        return texto_limpo

    def tira_stopwords_e_romanos(self, palavra:str):
        '''
        Retira stop words e números romanos.

        Variáveis de entrada:
            palavra: é uma string que contém uma palavra. Não funciona se colocar um texto.

        Variáveis de saída:
            out: é uma string vazia se a entrada era um número romano ou stop word. Se a entrada
            não era romano ou stop word, retorna a própria entrada.

        Obs: Em geral não é necessário modificar esse método.
        '''

        #recodifica em utf-8
        palavra = self.limpa_utf8(palavra)

        #remove stopwords
        if palavra in self.stop_words:
            return ''

        #se a palavra tem tamanho menor que 2 provavelmente não é importante
        if(len(palavra) < 2 ):
            return ''

        if (palavra == ''): return ''

        #se a palavra não é um número romano eu retorno a própia palavra.
        out = re.sub('[^mdclxvi]', '', palavra)
        if (len(out) != len(palavra)):
            return palavra

        #se chegou aqui é porque é um número romano
        return ''

    def importa_textos(self):
        '''Aqui você deve definir sua função de importar textos.
           Nesse método você deve inicializar os atributos 'textos' e 'textos_tratados'.

           Você pode/deve adicionar variáveis de entrada para esse método para se ajustar
           ao seu problema.
        '''

    def stem(self):
        '''
        Faz o stemming nas palavras utilizando o pacote nltk com o RSLP Portuguese stemmer.
        O resultado do stemming fica salvo no atributo textos_stem.

        Variáveis de entrada:
            None

        Variáveis de saída:
            None

        Obs: Em geral não é necessário modificar esse método.
        '''

        print('Comecou a fazer o stemming.')
        t = time.time()

        #inicializando o objeto stemmer
        stemmer = nltk.stem.RSLPStemmer()

        for texto in self.textos_tratados:
            #Faz o stemming para cada palavra na resolucao
            palavras_stemmed_texto = [stemmer.stem(word) for word in texto.split()]
            #Faz o append da resolucao que passou pelo stemming
            self.textos_stem.append(" ".join(palavras_stemmed_texto))

        print('Tempo para fazer o stemming: ' + str(time.time() - t) + '\n')


    def analisa_clusters(self, base_tfidf, id_clusters):
        '''
        Tenta visualizar as cluster definidas. Além disso retorna um dataframe
        que contém a informação do número de textos por cluster

        Variáveis de entrada:
            base_tfidf: é uma matriz obtida pela aplicação do tfidf no bag of
            words obtido a partir dos textos que passaram pelo stemmer. Não é a
            matriz com dimensionalidade reduzida.
            id_cluster: é um array que contém os identificadores de cada cluster.

        Variáveis de saída:
            cluster_n_textos: é um dataframe em que a primeira coluna está o identificador da cluster
            e na segunda coluna está o número de textos na cluster.

        Obs: Em geral não é necessário modificar esse método.
        '''

        clusters = np.unique(id_clusters)

        #inicializa o output da funcao
        n_textos = np.zeros(len(clusters)) #numero de textos pertencentes a uma cluster

        #reduz a dimensionalidade para 2 dimensoes
        base_tfidf_reduced = self.SVD(base_tfidf, dim=2)
        X = base_tfidf_reduced[:,0]
        Y = base_tfidf_reduced[:,1]

        colors = cm.rainbow(np.linspace(0, 1, len(n_textos)))

        for cluster, color in zip(clusters, colors):
            idxs = np.where(id_clusters == cluster) #a primeira cluster não é a 0 e sim a 1
            n_textos[cluster-1] = len(idxs[0])
            x = X[idxs[0]]
            y = Y[idxs[0]]
            plt.scatter(x, y, color=color)

        n_textos = pd.DataFrame(n_textos, columns=['numero de textos'])
        cluster_n_textos = pd.DataFrame(clusters,columns=['cluster_id']).join(n_textos)

        return cluster_n_textos

    def vec_tfidf(self, ngram_range:tuple=(1,1), stem:bool=True):
        '''
        Vetoriza e aplica o tfidf nos textos. Por padrão utiliza stemming. Se
        não quiser stemming é só mudar o parâmetro 'stem' para False.

        Variáveis de entrada:
            stem: é uma variável opcional. É um bool que diz se vai usar os textos
            com stemming ou não.

        Variáveis de saída:
            base_tfidf: matriz esparsa que contém a vetorização e aplicação do tfidf
            nos textos

        Obs: Em geral não é necessário modificar esse método.
        '''

        if stem:
            vec = CountVectorizer(ngram_range=ngram_range)
            bag_palavras = vec.fit_transform(self.textos_stem)
            feature_names = vec.get_feature_names()
            base_tfidf = TfidfTransformer().fit_transform(bag_palavras)
        else:
            vec = CountVectorizer()
            bag_palavras = vec.fit_transform(self.textos_tratados)
            feature_names = vec.get_feature_names()
            base_tfidf = TfidfTransformer().fit_transform(bag_palavras)

        return base_tfidf

    def SVD(self, base_tfidf, dim:int=500):
        '''
        Reduz a dimensionalidade dos dados de entrada.

        Variáveis de entrada:
            base_tfidf: base de dados a ter sua dimensionalidade reduzida.
            dim: é uma variável opcional. É um inteiro que corresponde ao número
            de dimensões desejada na saída.

        Variáveis de saída:
            base_tfidf_reduced: base de dados com dimensionalidade reduzida.

        Obs: Em geral não é necessário modificar esse método.
        '''

        print('Começou a redução de dimensionalidade.')
        t = time.time()
        if base_tfidf.shape[1] < dim: dim = base_tfidf.shape[1] - 1
        svd = TruncatedSVD(n_components = dim, random_state = 42)
        base_tfidf_reduced = svd.fit_transform(base_tfidf)
        print('Número de dimensões de entrada: ' + str(base_tfidf.shape[1]))
        print(str(dim) + ' dimensões explicam ' + str(svd.explained_variance_ratio_.sum()) + ' da variância.')
        elpsd = time.time() - t
        print('Tempo para fazer a redução de dimensionalidade: ' + str(elpsd) + '\n')
        return base_tfidf_reduced

    def generate_wordcloud(self, cluster:int, filename:str):
        '''
        Gera uma nuvem de palavras de uma cluster com identificador 'cluster_id'.

        Variáveis de entrada:
            cluster: é um inteiro que contém o identificador da cluster que se
            deseja fazer uma word cloud.
            filename: é o nome do arquivo csv que contém o identificador da
            cluster e o texto.

        Variáveis de saída:
            None

        Obs: Se você não modificou o formato dos csvs não é necessário modificar esse método.
        '''

        df = pd.read_csv(filename,sep='|')
        df_cluster = df[df['cluster_id'] == cluster]

        textos_da_cluster = list(df_cluster['textos_tratados'])

        textos_da_cluster = '\n'.join(textos_da_cluster)

        wordcloud = WordCloud().generate(textos_da_cluster)
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.show()

    def mostra_conteudo_cluster(self, filename:str, cluster:int, n_amostras:int=10, st:bool=1):
        '''
        Esse método cria um arquivo txt com 'n_amostras' aleatórias da cluster 'cluster'.

        Variáveis de entrada:
            filename: é uma string com o nome do csv a ser lido;
            cluster: é um inteiro que corresponde ao código da cluster que você
            deseja analisar;
            n_amostras: é um inteiro. É uma variável opcional em que você determina
            quantas amostras da cluster irá escrever no txt.

        Variáveis de saída:
            None

        Obs: Se você não modificou o formato dos csvs não é necessário modificar esse método.
        '''

        df = pd.read_csv(filename, sep='|')
        df_cluster = df[df['cluster_id'] == cluster]

        if df_cluster.shape[0] >= n_amostras:
            df_cluster_sample = df_cluster.sample(n_amostras)
        else:
            df_cluster_sample = df_cluster

        fo = open(r'conteudo_cluster'+str(cluster)+'_n_'+str(df_cluster.shape[0])+'.txt', 'w+')

        #Se for para escrever os textos sem tratamento
        if(st):
            for i in range(df_cluster_sample.shape[0]):
                fo.writelines(df_cluster_sample['textos_id'].iloc[i] + '\n')
                fo.writelines(df_cluster_sample['textos'].iloc[i])
                fo.writelines('\n\n')
        else:
            for i in range(df_cluster_sample.shape[0]):
                fo.writelines(df_cluster_sample['textos_id'].iloc[i] + '\n')
                fo.writelines(df_cluster_sample['textos_tratados'].iloc[i])
                fo.writelines('\n\n')

        fo.close()
    def generate_csvs(self):
        '''
        Crie aqui o método que cria csvs que serão utilizados para a análise dos resultados.

        É necessário que você crie um csv com as seguintes características:
            1.Uma coluna que contém o identificador do texto (o atributo textos_id).
            Essa coluna DEVE se chamar 'textos_id';
            2.Uma coluna que contém o códigos das clusters. Essa coluna DEVE se
            chamar 'cluster_id';
            3.Uma coluna que contém os textos tratados (o atributo textos_tratados).
            Essa coluna DEVE se chamar 'textos_tratados'.
            4. Uma coluna que contém os textos puros (o atributo textos). Essa
            coluna DEVE se chamar 'textos'
        '''
