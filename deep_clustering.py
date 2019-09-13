import numpy as np
import pickle
from scipy.cluster import hierarchy
import time
import matplotlib.pyplot as plt
import pandas as pd
from sklearn import preprocessing

X = np.load('mat.npy')
X = np.delete(X, (0), axis=0)
X = preprocessing.scale(X)

#Clustering
clusters_por_cosseno = hierarchy.linkage(X,"average", metric="cosine")
plt.figure()
dn = hierarchy.dendrogram(clusters_por_cosseno)
plt.savefig('dendogram.jpg')

limite_dissimilaridade = 6.5
id_clusters = hierarchy.fcluster(clusters_por_cosseno, limite_dissimilaridade, criterion="distance")

#Colocando o resultado em dataframes
clusters = np.unique(id_clusters)
n_normas = np.zeros(len(clusters)) #numero de normas pertencentes a uma cluster
for cluster in clusters:
    idxs = np.where(id_clusters == cluster) #a primeira cluster não é a 0 e sim a 1
    n_normas[cluster-1] = len(idxs[0])


tabela_macrotemas = pd.read_csv('Macrotemas_python.csv',sep='|').rename(columns={'Macrotema atual':'Macrotema_atual'})


res_names = list(tabela_macrotemas['Citadora'])
cluster_nnormas = pd.DataFrame(list(zip(clusters,n_normas)),columns=['cluster_id','n_normas'])
cluster_norma = pd.DataFrame(list(zip(id_clusters,res_names)), columns=['cluster_id','Citadora'])

macrotema_norma_ementa = tabela_macrotemas[['Assunto/Ementa','Macrotema_atual','Citadora']]


out = pd.merge(cluster_norma,macrotema_norma_ementa)
out.to_csv('out.csv',sep='|',index=False,encoding='utf-8')
'''
