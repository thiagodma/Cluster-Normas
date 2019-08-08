from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from scipy.cluster import hierarchy
import pandas as pd
from cluster_normas_funcoes import ClusterNormas
import time
import matplotlib.pyplot as plt

#Aqui eu crio uma instancia da classe ClusterNormas
cn = ClusterNormas()

#Aqui eu defino as stop words gerais e especificas para esse problema. O atributo stop_words foi definido.
cn.define_stop_words()

#Aqui eu carrego os atributos resolucoes, resolucoes_tratadas e nome_arquivos.
cn.importa_normas()

arquivos_fora_padrao=[]
for resolucao,nome_arquivo in zip(cn.resolucoes_tratadas,cn.nome_arquivos):
    if resolucao == 'norma fora de padrão':
        arquivos_fora_padrao.append(nome_arquivo)

#Faz o stemming e guarda o resultado no atributo resolucoes_stem
cn.stem()

#Vetorizando e aplicando o tfidf
vec = CountVectorizer()
bag_palavras = vec.fit_transform(cn.resolucoes_stem)
feature_names = vec.get_feature_names()
base_tfidf = TfidfTransformer().fit_transform(bag_palavras)
base_tfidf = base_tfidf.todense()

#Reduzindo a dimensionalidade
base_tfidf_reduced = cn.SVD(600, base_tfidf)

#Clustering
print('Começou a clusterização.')
t = time.time()
clusters_por_cosseno = hierarchy.linkage(base_tfidf_reduced,"average", metric="cosine") #pode testar metric="euclidean" também
plt.figure()
dn = hierarchy.dendrogram(clusters_por_cosseno)
limite_dissimilaridade = 0.92
id_clusters = hierarchy.fcluster(clusters_por_cosseno, limite_dissimilaridade, criterion="distance")
elpsd = time.time() - t
print('Tempo para fazer a clusterização: ' + str(elpsd) + '\n')

cluster_n_normas = cn.analisa_clusters(base_tfidf_reduced, id_clusters)

#Colocando em dataframes
X = pd.DataFrame(id_clusters,columns=['cluster_id'])
Y = pd.DataFrame(cn.nome_arquivos,columns=['norma'])
W = pd.DataFrame(list(range(len(cn.resolucoes_tratadas))), columns=['codigo_norma'])
# Matriz clusterização
Z = X.join(Y)
Z = Z.join(W)

print('Foram encontradas ' + str(max(Z['cluster_id'])) + ' clusters\n')

#Exporta as tabelas
Z.to_csv('cluster_normas_cosseno.csv', sep='|',
                    index=False, encoding='utf-8')
