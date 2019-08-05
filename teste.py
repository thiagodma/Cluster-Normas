
import cluster_normas_funcoes as cnf
import re
cnf.trata_textos(s,stop_words)


#re.findall(r'\nart. \d',texto)

#r'\nArt. 1(.*)\nArt. 5'

count = 0
for resolucao in resolucoes_tratadas:
    if resolucao == 'norma fora de padrão':
        count = count + 1