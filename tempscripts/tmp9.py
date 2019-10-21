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

def create_art_map(corp_iter, iop_object, pat='pat4', delim=10000):
    '''
    Function to create summury of the document by finding all used law articles.
    Results will be written to iop_object
    '''
    time = dbg.time()
    pattern0 = (
        '[А-я.]+ [0-9]{1,4}\.*[0-9]{0,4} '
        +'[А-я.]* [0-9]{1,4}\.*[0-9]{0,4} '
        +'[А-я.]+ [А-я.]+'
    )
    pattern1 = (
        '[А-я.]+ [0-9]{1,4}\.*[0-9]{0,4} *'
        +'[А-я.]* *[0-9]{1,4}\.*[0-9]{0,4} *'
        +'[А-я.]+ [А-я.]+'
    )
    pattern2 = (
        '[А-я.]+ [0-9]{1,4}\.*[0-9]{0,4} *'
        +'[А-я.]* *[0-9]{1,4}\.*[0-9]{0,4},* *'
        +'[0-9]{0,4}\.*[0-9]{0,4} *'
        +'[А-я.]+ [А-я.]+'
    )
    pattern3 = (
        '[А-я]*[,.:;]* *[А-я0-9.]*[,.:;]* *[А-я]*[,.:;]* *[А-я0-9.]*[,.:;]* *'
        +'[Сс]т[.атьяиеюёймх]{1,6} [0-9]{1,4}\.*[0-9]{0,4}\W* *'
        +'[0-9]{0,4}\.*[0-9]{0,4}\W* *[0-9]{0,4}\.*[0-9]{0,4}\W* '
        +'[А-я]+ [А-я]* *\w+ [А-я0-9\-ФКЗ]*'
    )
    pattern4 = (
        '[А-я0-9N\-.]*\W{0,2}[А-я0-9N\-.]+\W{1,2}[Сс]т[а.]\w* '
        +'[0-9]{1,4}\.*[0-9]{0,4}\W{1,2}[А-я0-9N\-]+\W{1,2}'
        +'[А-я0-9N\-]+\W{1,2}[А-я0-9N\-]+\W{1,2}[А-я0-9N\-]+\W{1,2}'
    )
    pattern5 = (
        '[А-я0-9N\-.]*\W{0,2}[А-я0-9N\-.]+\W{1,2}[Сс]т[а.]\w* [0-9]{1,4}\.*[0-9]{0,4}\W{1,2}[А-я0-9N\-]+\W{1,2}[А-я0-9N\-]+\W{1,2}[А-я0-9N\-]*\W{0,2}[А-я0-9N\-]*\W{0,2}'
    )
    options = {
        'pat0': pattern0,
        'pat1': pattern1,
        'pat2': pattern2,
        'pat3': pattern3,
        'pat4': pattern4,
        'pat5': pattern5
    }
    months = [
        'янва', 'февр', 'март',
        'апре', 'мая', 'июня',
        'июля', 'авгу', 'сентяб',
        'октяб', 'ноябр', 'декабр'
    ]
    for iind, item in enumerate(corp_iter):
        if iind % delim == 0:
            print('\t', 'doc#', iind, 'time:', '{: >6.2f}'.format(dbg.time()-time))
        doc = item['Текст документа']
        cleaned = re.findall(options[pat], doc)
        for ind in list(range(len(cleaned)-1, -1, -1)):
            for month in months:
                if month in cleaned[ind]:
                    cleaned.pop(ind)
                    break
        iop_object.append(cleaned)
    
    
#pattern2 = (
#'[А-я]*[,.:;]* *[А-я0-9.]*[,.:;]* *[А-я]*[,.:;]* *[А-я0-9.]*[,.:;]* *[Сс]т[.атьяиеюёймх]{1,6} [0-9]{1,4}\.*[0-9]{0,4}\W* *[0-9]{0,4}\.*[0-9]{0,4}\W* *[0-9]{0,4}\.*[0-9]{0,4}\W* [А-я]+ [А-я]* *\w+ [А-я0-9\-ФКЗ]*'
#)
#


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