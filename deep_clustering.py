import numpy as np
import pickle
from scipy.cluster import hierarchy
import time
import matplotlib.pyplot as plt
import pandas as pd
from sklearn import preprocessing

X = np.load('X_clas.npy')

#Todas as features com média 0 e desvio padrão 1
X = preprocessing.scale(X)

#Importa o vetor de importância das features
fi = np.load('fi.npy')

#Incorpora a importância das features
for i in range(X.shape[1]):
    X[:,i] = X[:,i]*fi[i]

data = pd.read_csv('Data_cluster_articles_v2.csv',sep='|',encoding='utf-8',index_col=False)

macrotemas = list(data['macrotemas'])
unique_macrotemas = list(dict.fromkeys(macrotemas))

for unique_macrotema in unique_macrotemas:

    unique_macrotema='medicamentos'
    idx = data['macrotemas']==unique_macrotema
    X_macrotema = X[idx]
    #Clustering
    clusters_por_cosseno = hierarchy.linkage(X_macrotema,"average", metric="cosine",optimal_ordering=True)
    #plt.figure()
    #dn = hierarchy.dendrogram(clusters_por_cosseno)
    #plt.savefig('dendogram.jpg')
    #break
    limite_dissimilaridade = 0.7
    id_clusters = hierarchy.fcluster(clusters_por_cosseno, limite_dissimilaridade, criterion="distance")

    #Colocando o resultado em dataframes
    clusters = np.unique(id_clusters)
    n_normas = np.zeros(len(clusters)) #numero de normas pertencentes a uma cluster
    for cluster in clusters:
        idxs = np.where(id_clusters == cluster)
        n_normas[cluster-1] = len(idxs[0])


    cluster_nnormas = pd.DataFrame(list(zip(clusters,n_normas)),columns=['cluster_id','n_normas'])

    id_clusters = pd.DataFrame(id_clusters,columns=['cluster_id'])
    data = data[data['macrotemas']==unique_macrotema].reset_index()
    del data['index']
    data = data.join(id_clusters)

    break
