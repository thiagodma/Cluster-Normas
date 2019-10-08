import numpy as np
import pickle
from scipy.cluster import hierarchy
import time
import matplotlib.pyplot as plt
import pandas as pd
from sklearn import preprocessing
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

X = np.load('X_clas.npy')
X = preprocessing.scale(X)
data = pd.read_csv('Data_cluster.csv',sep='|',encoding='utf-8')
macrotema_por_norma = list(data['macrotemas'])

macrotemas = list(dict.fromkeys(macrotema_por_norma))

di = dict.fromkeys(macrotema_por_norma)
i=0
for macrotema in macrotemas:
    di[macrotema] = i
    i+=1

y = np.zeros(len(macrotema_por_norma))
i=0
for m in macrotema_por_norma:
    y[i] = di[m]
    i+=1

X_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=0.2, random_state=42)

clf = RandomForestClassifier(n_estimators=200,max_depth=200, random_state=42)
clf.fit(X_train,y_train)
print(clf.score(X_valid,y_valid))
fi = clf.feature_importances_
np.save('fi', fi)
