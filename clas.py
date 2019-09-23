import numpy as np
import pickle
from scipy.cluster import hierarchy
import time
import matplotlib.pyplot as plt
import pandas as pd
from sklearn import preprocessing
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

X = np.load('X_LM.npy')
X = preprocessing.scale(X)
with open("macrotema_por_norma.txt", "rb") as fp:
    macrotema_por_norma = pickle.load(fp)

macrotema_por_norma = [m.lower() for m in macrotema_por_norma]
macrotemas = list(dict.fromkeys(macrotema_por_norma))

di = dict.fromkeys(macrotema_por_norma)
i=0
for macrotema in macrotemas:
    di[macrotema] = i
    i+=1

y = np.zeros(len(macrotema_por_norma))
i=0
for m in macrotema_por_norma:
    #import pdb; pdb.set_trace()
    y[i] = di[m]
    #import pdb; pdb.set_trace()
    i+=1

#import pdb; pdb.set_trace()
X_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=0.2, random_state=42)

clf = RandomForestClassifier(n_estimators=200,max_depth=20)
clf.fit(X_train,y_train)
print(clf.score(X_valid,y_valid))
fi = clf.feature_importances_
np.save('fi', fi)
