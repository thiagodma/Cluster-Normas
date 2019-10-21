from classic_clustering import *
from collections import Counter

class ClusterNormas(ClassicClustering):

    def __init__(self,filename:str):
        ClassicClustering.__init__(self)
        self.df = pd.read_csv(filename, sep='|', encoding='utf-8')
        self.df[self.df.artigos != 'norma fora de padrao']
        self.df = self.df[self.df['macrotemas'] == 'medicamentos']

    def importa_textos(self):
        print('\nComeçou a importação dos textos.')

        self.textos = list(self.df.artigos)

        t = time.time()
        self.textos_tratados = [self.trata_textos(texto) for texto in self.textos]
        self.textos_id = ['P' + str(i) for i in range(len(self.textos_tratados))]
        elpsd = time.time() - t
        print('Tempo para processar os textos: ' + str(elpsd))

    def generate_csvs(self, cluster_n_textos, id_clusters):

        textos_por_cluster = pd.DataFrame(zip(list(self.df.nomes_normas),
                             list(id_clusters),self.textos,self.textos_tratados),
                             columns=['normas','cluster_id','textos','textos_tratados'])

        word_count = [self.freq_words_cluster(cluster,textos_por_cluster,5) for cluster in cluster_n_textos.cluster_id]

        cluster_n_textos['palavras_importantes'] = word_count
        info_cluster = cluster_n_textos

        info_cluster.to_csv('info_cluster.csv', sep='|',index=False, encoding='utf-8')
        textos_por_cluster.to_csv('textos_por_cluster.csv', sep='|',index=False, encoding='utf-8')

        return textos_por_cluster

    def freq_words_cluster(self, cluster_id:int, textos_por_cluster:df, qtd:int):

        artigos_tratados = list((textos_por_cluster[textos_por_cluster.cluster_id==cluster_id]).textos_tratados)
        all_words = ''
        for i in range(len(artigos_tratados)):
            all_words = all_words + artigos_tratados[i] + ' '

        Counter = Counter(all_words)
        most_occur = Counter.most_common(qtd)

        out = [item [0] for item in most_occur]

        return ' '.join(out)
