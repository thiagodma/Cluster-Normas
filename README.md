# Clusterização das normas da Anvisa.

Foi finalizada a abordagem clássica para fazer clusterização de texto. Foi feito um forte pré-processamento colocando todas as letras como minúsculas, retirando pontuações, retirando stop words etc. Após o pré processamento, um bag of words é gerado e é aplicado o tfidf nesse bag of words. Após isso, fazemos uma redução de dimensionalidade usando o Truncated SVD. Por fim, o algoritmo de clusterização escolhido é o hierarchical clustering.

Os resultados estão dispostos nos arquivos info_cluster.csv, que contém o código de cada cluster e o número de normas pertencentes a essa cluster, e cluster_normas_cosseno.csv, que contém a referência para a norma e a informação de a qual cluster essa norma pertence.
