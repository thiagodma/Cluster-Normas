from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from scipy.cluster import hierarchy
from datetime import datetime
import pandas as pd
import cluster_normas_funcoes as cnf
import matplotlib.pyplot as plt

# Controle de tempo
ti = datetime.now()
print('Iniciado as: ' + str(ti) + '\n') 

stop_words = [cnf.limpa_utf8(w) for w in cnf.stop_words]

# Input de arquivos
resolucoes, nome_arquivos = cnf.importa_normas()

#Faz o stemming
resolucoes_stem = cnf.stem(resolucoes)

#Checando o tempo para importar e tratar os textos
timport = datetime.now()
print('Tempo para importar e tratar textos: ', timport - ti)

#Vetorizando
vec = CountVectorizer()
bag_palavras = vec.fit_transform(resolucoes_stem)
feature_names = vec.get_feature_names()
base_tfidf = TfidfTransformer().fit_transform(bag_palavras)

#Tornando a matriz densa
base_tfidf = base_tfidf.todense()

#Reduzindo a dimensionalidade
base_tfidf_reduced = cnf.SVD(500, base_tfidf)

#Clustering
clusters_por_cosseno = hierarchy.linkage(base_tfidf_reduced,"average", metric="cosine") #pode testar metric="euclidean" também
plt.figure()
dn = hierarchy.dendrogram(clusters_por_cosseno)

# Separa a que Cluster pertence cada texto, pela ordem na lista de textos,
# dado o parâmetro de limite de dissimilaridade threshold
limite_dissimilaridade = 0.85
id_clusters = hierarchy.fcluster(clusters_por_cosseno, limite_dissimilaridade, criterion="distance")

analise = cnf.analisa_clusters(base_tfidf_reduced, id_clusters)

#Colocando em dataframes
X = pd.DataFrame(id_clusters,columns=['cluster_id'])
Y = pd.DataFrame(nome_arquivos,columns=['norma'])

# Matriz clusterização
Z = X.join(Y)

print('Foram encontradas ' + str(max(Z['cluster_id'])) + ' clusters\n')

#Exporta as tabelas
Z.to_csv('cluster_normas_cosseno.csv', sep='|', 
                    index=False, encoding='utf-8')

#Printa o tempo total de execução do script
print('Tempo total: ',datetime.now() - ti)