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

        word_count = [self.freq_words_cluster(cluster,textos_por_cluster,10) for cluster in cluster_n_textos.cluster_id]

        cluster_n_textos['palavras_importantes'] = word_count
        info_cluster = cluster_n_textos

        info_cluster.to_csv('info_cluster.csv', sep='|',index=False, encoding='utf-8')
        textos_por_cluster.to_csv('textos_por_cluster.csv', sep='|',index=False, encoding='utf-8')

        return textos_por_cluster,info_cluster

    def freq_words_cluster(self, cluster_id:int, textos_por_cluster, qtd:int):

        artigos_tratados = list((textos_por_cluster[textos_por_cluster.cluster_id==cluster_id]).textos_tratados)

        all_words = []
        for artigo in artigos_tratados:
            for palavra in re.split(' ',artigo):
                if palavra is not '': all_words.append(palavra)

        counter = Counter(all_words)
        most_occur = counter.most_common(qtd)
        out = [item[0] for item in most_occur]

        return ' '.join(out)

    def palavras2normas(self,palavras:list):

        info_cluster = pd.read_csv('info_cluster.csv',sep='|',encoding='utf-8')
        textos_por_cluster = pd.read_csv('textos_por_cluster.csv',sep='|',encoding='utf-8')

        #aqui eu vejo quantas vezes as palavras dadas aparecem em cada cluster
        count = np.zeros(info_cluster.shape[0])
        for i in range(info_cluster.shape[0]):
            keywords = re.split(' ',info_cluster.palavras_importantes.iloc[i])
            for palavra in palavras:
                count[i] = count[i] + (palavra in keywords)

        #pego so as cluster que dão match com as palavras solicitadas
        idxs = np.where(count == len(palavras))[0]

        if len(idxs) == 0:
            print('Deu ruim!')
            return

        all_count = []
        all_normas = []
        for idx in idxs:
            aux = textos_por_cluster[textos_por_cluster.cluster_id == idx+1]
            normas = []
            #o contador agora é para cada norma
            count = np.zeros(len(np.unique(aux.normas)))
            #iterando nos artigos dentro de uma cluster
            #import pdb; pdb.set_trace()
            for i in range(aux.shape[0]):
                #se essa norma ainda não apareceu
                #import pdb; pdb.set_trace()
                if aux.normas.iloc[i] not in normas: normas.append(aux.normas.iloc[i])
                #conto o número de vezes que as palavras dadas aparecem na norma sendo analisada
                for palavra in palavras:
                    count[len(normas)-1] += (palavra in aux.textos_tratados.iloc[i])
            all_count.extend(list(count))
            all_normas.extend(normas)

        sorted_idxs = np.argsort(all_count)
        #esse array ta ordenado em ordem crescente
        sorted_normas = [all_normas[idx] for idx in sorted_idxs]
        #mas eu quero em ordem decrescente
        return list(reversed(sorted_normas))
