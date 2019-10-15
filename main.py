from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from scipy.cluster import hierarchy
import pandas as pd
from cluster_normas import ClusterNormas
import time
import matplotlib.pyplot as plt
import numpy as np

#Aqui eu crio uma instancia da classe ClusterNormas
cn = ClusterNormas()

#Aqui eu defino as stop words gerais e especificas para esse problema. O atributo stop_words foi definido.
cn.define_stop_words()

#Aqui eu carrego os atributos resolucoes, resolucoes_tratadas e nome_arquivos.
cn.importa_textos()

#Faz o stemming e guarda o resultado no atributo resolucoes_stem
cn.stem()

#vetoriza e aplica o tfidf
base_tfidf = cn.vec_tfidf()

#Reduzindo a dimensionalidade
base_tfidf_reduced = cn.SVD(base_tfidf,dim=600)

#Clustering
print('Começou a clusterização.')
t = time.time()
clusters_por_cosseno = hierarchy.linkage(base_tfidf_reduced,"average", metric="cosine")
plt.figure()
dn = hierarchy.dendrogram(clusters_por_cosseno)
plt.savefig('dendogram.jpg')
'''
limite_dissimilaridade = 0.92
id_clusters = hierarchy.fcluster(clusters_por_cosseno, limite_dissimilaridade, criterion="distance")
elpsd = time.time() - t
print('Tempo para fazer a clusterização: ' + str(elpsd) + '\n')

macrotema_cluster_nnormas = cn.analisa_clusters(base_tfidf_reduced, id_clusters, macrotema)

Z = pd.DataFrame(list(zip(macrotema_list, id_clusters, )))

#Colocando em dataframes
X = pd.DataFrame(id_clusters,columns=['cluster_id'])
Y = pd.DataFrame(cn.nome_arquivos,columns=['norma'])
W = pd.DataFrame(list(range(len(cn.resolucoes_tratadas))), columns=['codigo_norma'])
# Matriz clusterização
Z = X.join(Y)
Z = Z.join(W)

print('Foram encontradas ' + str(max(Z['cluster_id'])) + ' clusters\n')

#Exporta as tabelas
Z.to_csv('cluster_normas_cosseno.csv', sep='|',index=False, encoding='utf-8')
'''
