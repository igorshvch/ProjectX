import re
import random

import debugger as dbg

@dbg.timer_with_func_name
def find_demands(corp_iter):
    demands = []
    errors = []
    for ind, doc in enumerate(corp_iter):
        if ind % 10000 == 0:
            print('Docs:', ind)
        text = doc['Текст документа']
        re_obj = re.search(
            r'\n([Уу]становил:\n.*|[Уу]становила:\n.*).*(?=\.\n)',
            text
        )
        if re_obj:
            demands.append(re_obj.group())
        else:
            errors.append(ind)
    return demands, errors

def print_random_error(corp_iter, errors):
    def inner_f(start=0, lng=400, num=None):
        if not num:
            numb = errors[random.randint(0, len(errors)-1)]
            print(numb)
        else:
            numb = num
        print(corp_iter[numb]['Текст документа'][start:lng])
    return inner_f

def create_first_word_dct(corp_iter):
    dct = {}
    split_docs = []
    for d in corp_iter:
        d = d.lower()
        #d = d.replace('\n', ' ')
        d = re.findall(r'[а-я0-9][а-я0-9-]*', d)
        dct.setdefault(d[1], []).append(d)
        split_docs.append(d)
    return dct, split_docs


#cp3 = crp.CorpusBuffer(demands_meta['dcts'].nf_tag, word_len=2, POSes={'NOUN', 'ADJF', 'ADJS', 'COMP', 'VERB', 'INFN', 'PRTF', 'PRTS', 'GRND', 'NUMR', 'ADVB', 'NPRO', 'PRED', 'PREP'}, stop_words={'гггга', 'копа', 'рубль', 'коап', 'год', 'размер', 'число', 'сумма', 'административный', 'россия', 'москва',})
#
#ddct = gsm.corpora.Dictionary(cp3(doc) for doc in demands_meta['iter_lm'])
#
#ddct_tfidf = gsm.models.TfidfModel(ddct.doc2bow(cp3(doc)) for doc in demands_meta['iter_lm'])
#
#tfidf_corp = list(ddct_tfidf[doc2] for doc2 in (ddct.doc2bow(cp3(doc)) for doc in demands_meta['iter_lm']))
#
#lda_m = gsm.models.LdaMulticore(tfidf_corp, id2word=ddct, num_topics=7)
#
#lda_m.print_topics(num_words=16)