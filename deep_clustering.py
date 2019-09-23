import numpy as np
import pickle
from scipy.cluster import hierarchy
import time
import matplotlib.pyplot as plt
import pandas as pd
from sklearn import preprocessing

X = np.load('X_LM.npy')

#Todas as features com média 0 e desvio padrão 1
X = preprocessing.scale(X)

#Importa o vetor de importância das features
fi = np.load('fi.npy')

#Incorpora a importância das features
for i in range(X.shape[1]):
    X[:,i] = X[:,i]/fi[i]

with open('res.txt','rb') as fp: texts = pickle.load(fp)
with open('res_nome.txt','rb') as fp: res_nomes = pickle.load(fp)
with open('macrotema_por_norma.txt','rb') as fp: macrotemas_por_norma = pickle.load(fp)


#Clustering
clusters_por_cosseno = hierarchy.linkage(X,"average", metric="cosine")
#plt.figure()
#dn = hierarchy.dendrogram(clusters_por_cosseno)
#plt.savefig('dendogram.jpg')

limite_dissimilaridade = 0.9
id_clusters = hierarchy.fcluster(clusters_por_cosseno, limite_dissimilaridade, criterion="distance")

#Colocando o resultado em dataframes
clusters = np.unique(id_clusters)
n_normas = np.zeros(len(clusters)) #numero de normas pertencentes a uma cluster
for cluster in clusters:
    idxs = np.where(id_clusters == cluster) #a primeira cluster não é a 0 e sim a 1
    n_normas[cluster-1] = len(idxs[0])


cluster_nnormas = pd.DataFrame(list(zip(clusters,n_normas)),columns=['cluster_id','n_normas'])
cluster_norma = pd.DataFrame(list(zip(id_clusters,res_nomes,texts,macrotemas_por_norma)), columns=['cluster_id','Citadora','Texto_Completo','Macrotema'])
