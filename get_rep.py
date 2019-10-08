from fastai import *
from fastai.text import *

data_clas = load_data('.','data_clas')
learn_clas = text_classifier_learner(data_clas, AWD_LSTM, drop_mult=0.5, callback_fns=ShowGraph, pretrained=False)
learn_clas.load('learn_clas_ft')

resolucoes = list(pd.read_csv('Data_cluster.csv',sep='|',encoding='utf-8')['textos'])

mbe = learn_clas.model[0]

def masked_concat_pool(outputs, mask):
    "Pool MultiBatchEncoder outputs into one vector [last_hidden, max_pool, avg_pool]."
    output = outputs[-1]
    avg_pool = output.masked_fill(mask[:, :, None], 0).mean(dim=1)
    avg_pool *= output.size(1) / (output.size(1)-mask.type(avg_pool.dtype).sum(dim=1))[:,None]
    max_pool = output.masked_fill(mask[:,:,None], -float('inf')).max(dim=1)[0]
    x = torch.cat([output[:,-1], max_pool, avg_pool], 1)
    return x

X = np.zeros((1,1200))
texts = []
for resolucao in resolucoes:
    xb,yb = learn_clas.data.one_item(resolucao)
    sentence = torch.cuda.LongTensor(xb.tolist()[0]).unsqueeze(0)
    raw_outputs, outputs, masks = mbe.forward(sentence)
    sentence_rep = masked_concat_pool(outputs, masks)
    X = np.append(X,sentence_rep,axis=0)

X = np.delete(X, (0), axis=0)
np.save('X_clas', X)
