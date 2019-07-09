from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from scipy.cluster import hierarchy
from datetime import datetime
import pandas as pd
import cluster_normas_funcoes as cnf

# Controle de tempo
ti = datetime.now()
print('Iniciado as: ',ti) 

stop_words = [cnf.limpa_utf8(w) for w in cnf.stop_words]

# Input de arquivos
resolucoes, nome_arquivos = cnf.importa_normas()

#Checando o tempo para importar e tratar os textos
timport = datetime.now()
print('Tempo para importar e tratar textos: ', timport - ti)

#Vetorizando
bag_palavras = CountVectorizer().fit_transform(resolucoes)
del(resolucoes)
base_tfidf = TfidfTransformer().fit_transform(bag_palavras)
del(bag_palavras)


#Clustering
base_tfidf = base_tfidf.todense()

clusters_por_cosseno = hierarchy.linkage(base_tfidf,"average", metric="cosine") #pode testar metric="euclidean" também

# Separa a que Cluster pertence cada texto, pela ordem na lista de textos,
# dado o parâmetro de limite de dissimilaridade threshold
limite_dissimilaridade = 0.85
id_clusters = hierarchy.fcluster(clusters_por_cosseno, limite_dissimilaridade, criterion="distance")

#Colocando em dataframes
X = pd.DataFrame(id_clusters,columns=['cluster_id'])
Y = pd.DataFrame(nome_arquivos,columns=['norma'])

# Matriz clusterização
Z = X.join(Y)
 
#Exporta as tabelas
Z.to_csv('cluster_normas_cosseno.csv', sep='|', 
                    index=False, encoding='utf-8')

print('Foram encontradas ' + str(max(Z['cluster_id'])) + ' clusters\n')

#Printa o tempo total de execução do script
print('Tempo total: ',datetime.now() - ti)