#Importando os pacotes que seraoo utilizados
from stop_words import get_stop_words
from docx import Document
import os, os.path, glob, re, unicodedata, time
#==============================================================================


#Definindo algumas variaveis que serao uteis
#Dicionario para normalizacao dos nomes de arquivos
tipos_norma = {'PRT':'Portaria', 'RDC':'RDC', 'RES':'RE', 'RE':'RE', 
               'IN':'IN', 'INC':'INC', 'PRTC':'PRTC'}

# stop-words provisorio
stop_words = get_stop_words('portuguese') + ['','art','dou','secao','pag','pagina']

# Aprimorar romanos
#romanos_t0 = [' i ','ii','iii',' iv ',' v ',' vi ','vii','viii',' ix ',' x ',
#           ' xi ','xii','xiii']

base_romanos = ['i','v','x','l','c']


#==============================================================================


#Definindo as funcoes da biblioteca

# Recodificacao em utf8, removendo cedilhas acentos e coisas de latin
def limpa_utf8(palavra):    

    # Unicode normalize transforma um caracter em seu equivalente em latin.
    nfkd = unicodedata.normalize('NFKD', palavra)
    palavraSemAcento = u"".join([c for c in nfkd if not unicodedata.combining(c)])

    # Usa expressao regular para retornar a palavra apenas com numeros, letras e espaco
    #return re.sub('[^a-zA-Z/ \\\]', '', palavraSemAcento)
    return re.sub('[^a-zA-Z]', '', palavraSemAcento)


# Funcao de remocao de algarismos Romanos
def romanos_lento(palavra_original):
    palavra = limpa_utf8(palavra_original)
    
    # Nada que tenha um so caracter interessa
    if len(palavra) < 2: return ''
    # Se for grande, dificilmente sera um romano
    if len(palavra) > 5: return palavra
    
    # Vamos testar agora se eh um algasrismo romano
    for letra in palavra:
        if letra not in base_romanos:
            # Se alguma letra nao for romano da base de romanos, entao retorna
            return palavra

    # Se nao retornou antes, entao as poucas letras estao todas no grupo de romanos, vamos descartar
    return ''

# Tratamento principal: prepara o texto para contagem
def trata_textos(texto_limpo):
    # Remove digitos
    texto_limpo = re.sub("\d", " ", texto_limpo)
    
    # Minuscula
    texto_limpo = texto_limpo.lower()
    
    # Remove pontuacaoo e quebras de linha
    #texto_limpo = re.sub('[\n\r]', '', texto_limpo)
    #texto_limpo = re.sub(r'([^\s\w]|_)+', '', texto_limpo)
        
    # So a partir daqui o texto vira lista mesmo    
    texto_limpo = texto_limpo.split(' ')
    
    # Vamos atacar os romanos
    texto_limpo = [romanos_lento(w) for w in texto_limpo]
    
    #tira stop-words
    texto_limpo = [w for w in texto_limpo if w not in stop_words]
    
    # retorna o texto simplificado
    texto_limpo = ' '.join(texto_limpo)
    
    # Tratamento meio boca para i ii iii
    texto_limpo = re.sub('i+','i', texto_limpo)
    
    return texto_limpo


# Esta funcao serve para transformar o nome do arquivo em um formato 
# Tipo_norma numero_norma/AAAA (sem separadores de milhar)
def normaliza_nome_arquivo(nome_arq):
    # Este eh o dicionario para normalizar os nomes de normas
    global tipos_norma
    n_tratado = nome_arq
    # Procura o ultimo digito do nome do arquivo
    acha_digitos = re.match('.+([0-9])[^0-9]*$', nome_arq)
    # Posicao do ultimo digito encontrada
    pos_ultimo_digito = acha_digitos.start(1)
    # Corta o resto alem do ultimo di­gito
    nome_arq = nome_arq[:pos_ultimo_digito + 1]
    # Separa no split por underline
    nome_arq = nome_arq.split('_')
    # Parada de emergencia para nome de arquivos fora do padrao 
    if len(nome_arq) < 3:
        raise ValueError('Nome de arquivo fora de padrao:', n_tratado)
    # Monta nome_arq em norma_citadora no padrao desejado tipo_norma numero_norma/AAAA
    # JÃ¡ Ã© aplicado tambem o dicionario tipos_norma ao nome_arq[0], normalizando
    # assim o tipo da norma
    numeracao = nome_arq[-2].strip()
    # Adicionando o '0' Ã s normas que sao numeral unico, como IN 1/2014
    if len(numeracao) == 1: numeracao = '0' + numeracao     
    norma_citadora = tipos_norma[nome_arq[0].strip()] + ' ' + numeracao + '/' + nome_arq[-1]
    # Retorna nome_arq normalizado
    return norma_citadora 


# Importa arquivos
def importa_normas():
    #path ='Z:\\GGREG_GERAL\\#GECOR\\Inteligencia Regulatoria\\Normativo Compilado Anvisa - Painel\\Arquivos DOCX - atual - fevereiro.2019'
    path = 'Arquivos DOCX - atual - fevereiro.2019'
    #path ='C:\\Users\\paulo.gferreira\\Desktop\\Python\\Normas\\Normativos2'
    os.chdir(path)
    
    # Lista de pastas no diretorio atual
    pastas = [name for name in os.listdir('.')]
    
    arquivos = []
    resolucoes = []
    nome_arquivos = []
    
    for i in range(0,len(pastas)):
        # Faz o diretorio mudar para a pasta de cada ano
        os.chdir(pastas[i])
        # Pega todos os arquivos da pasta
        arquivos = glob.glob('*.docx')
        print('A pasta ' + str(i) + ' tem ' + str(len(arquivos)) + ' arquivos')
        t = time.time()
        for w in range(0, len(arquivos)):
            doc = Document(arquivos[w])
            doc.paragraphs
            texto = [parag.text for parag in doc.paragraphs]
            texto = '\n'.join(texto)
            # Substituicoes para desonerar o vetor Start, legado
            resolucoes.append(trata_textos(texto))
            nome_arquivos.append(normaliza_nome_arquivo(arquivos[w]))
            
        elapsed = time.time() - t
        print('Tempo para importar a pasta ' + str(i) + ': ' + str(elapsed) + '\n')
        os.chdir('..')
    #volta para o diretorio inicial
    os.chdir('..')
    return resolucoes, nome_arquivos

# Manobra de protecao do WorkDir para evitar dor de cabeca
def retorna_dir():
    abspath = os.path.abspath("__file__")
    dname = os.path.dirname(abspath)
    os.chdir(dname)

#==============================================================================