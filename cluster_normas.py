from classic_clustering import *

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
        self.textos_tratados = [self.trata_textos(artigo) for artigo in self.textos]
        self.textos_id = [self.df.nomes_normas.iloc[i] for i in range(self.df.shape[0])]
        elpsd = time.time() - t
        print('Tempo para processar os textos: ' + str(elpsd))
