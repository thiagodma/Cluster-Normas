import numpy as np
import pickle
from scipy.cluster import hierarchy
import time
import matplotlib.pyplot as plt
import pandas as pd
from sklearn import preprocessing
from sklearn.decomposition import TruncatedSVD

def getKSimilarTexts(norma:str,macrotema=None, k:int=5):

    X = np.load('X_LM.npy')

    #Todas as features com média 0 e desvio padrão 1
    X = preprocessing.scale(X)

    #Garantindo todos os vetores com norma 1
    #for i in range(X.shape[0]):
    #    Xi = X[i,:]
    #    X[i,:] = Xi/(np.sum(Xi**2)**0.5)

    data = pd.read_csv('Data_cluster.csv',sep='|',encoding='utf-8',index_col=False)
    macrotemas = np.unique(data.macrotemas)


    idx = np.where(data.nomes_normas==norma)[0]
    if len(idx)==0:
        print('Esta norma não está em nosso estoque.')
        return

    X_n = X[idx]
    aux = np.zeros(X.shape) + X_n
    similarity = np.sum(aux*X,axis=1)

    if isinstance(macrotema,str):
        idxs = np.where(data.macrotemas==macrotema)[0]
        similarity = similarity[idxs]
        data = data.loc[data.macrotemas==macrotema].reset_index()
        del data['index']
        if data.shape[0]==0:
            print('Não encontramos o macrotema solicitado. Lista de macrotemas disponíveis:')
            print(macrotemas)
            return

    idxs_max = similarity.argsort()[-k:][::-1]
    out = data.loc[idxs_max]
    return out

# RDC 16_2007, RDC 34_2008, RDC 259_2002
out = getKSimilarTexts('RDC 34_2008',macrotema='medicamentos',k=10)
out
print(out.ementas.iloc[8])
