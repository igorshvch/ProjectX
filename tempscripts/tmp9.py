import re
import random
from collections import Counter

import debugger as dbg
from writer import writer

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
        r'[А-я.]+ [0-9]{1,4}\.*[0-9]{0,4} '
        +r'[А-я.]* [0-9]{1,4}\.*[0-9]{0,4} '
        +r'[А-я.]+ [А-я.]+'
    )
    pattern1 = (
        r'[А-я.]+ [0-9]{1,4}\.*[0-9]{0,4} *'
        +r'[А-я.]* *[0-9]{1,4}\.*[0-9]{0,4} *'
        +r'[А-я.]+ [А-я.]+'
    )
    pattern2 = (
        r'[А-я.]+ [0-9]{1,4}\.*[0-9]{0,4} *'
        +r'[А-я.]* *[0-9]{1,4}\.*[0-9]{0,4},* *'
        +r'[0-9]{0,4}\.*[0-9]{0,4} *'
        +r'[А-я.]+ [А-я.]+'
    )
    pattern3 = (
        r'[А-я]*[,.:;]* *[А-я0-9.]*[,.:;]* *[А-я]*[,.:;]* *[А-я0-9.]*[,.:;]* *'
        +r'[Сс]т[.атьяиеюёймх]{1,6} [0-9]{1,4}\.*[0-9]{0,4}\W* *'
        +r'[0-9]{0,4}\.*[0-9]{0,4}\W* *[0-9]{0,4}\.*[0-9]{0,4}\W* '
        +r'[А-я]+ [А-я]* *\w+ [А-я0-9\-ФКЗ]*'
    )
    ####Following patterns give best results on EC court practice.
    pattern4 = (
        r'[А-я0-9N\-.]*\W{0,2}[А-я0-9N\-.]+\W{1,2}[Сс]т[а.]\w* '
        +r'[0-9]{1,4}\.*[0-9]{0,4}\W{1,2}[А-я0-9N\-]+\W{1,2}'
        +r'[А-я0-9N\-]+\W{1,2}[А-я0-9N\-]+\W{1,2}[А-я0-9N\-]+\W{1,2}'
    )
    ####Pattern # 5 is slightly more accurate but takes more time to compute
    pattern5 = (
        r'[А-я0-9N\-.]*\W{0,2}[А-я0-9N\-.]+\W{1,2}[Сс]т[а.]\w* [0-9]{1,4}\.*[0-9]{0,4}\W{1,2}[А-я0-9N\-]+\W{1,2}[А-я0-9N\-]+\W{1,2}[А-я0-9N\-]*\W{0,2}[А-я0-9N\-]*\W{0,2}'
    )
    ####
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
    
def create_parser(parser, number='sing'):
    '''
    Creating morphological analyzer to incline words.
    Two optiona re availble:
    - incline singular word form
    - incline plural word form
    '''
    def inner_sing(word):
        res = []
        lex_res = parser(word).lexeme
        for lex_mode in lex_res:
            if 'sing' in lex_mode.tag:
                res.append(lex_mode[0])
        return res
    def inner_plur(word):
        res = []
        lex_res = parser(word).lexeme
        for lex_mode in lex_res:
            if 'plur' in lex_mode.tag:
                res.append(lex_mode[0])
        return res
    options = {
        'sing': inner_sing,
        'plur': inner_plur
    }
    return options[number]

def collect_art_dispers(counter, lng, verbose=False):
    '''
    Returns:
    [
        #Article | % of all articles
        ('213', 0.3333333333333333),
        ('11', 0.16666666666666666),
        ('22', 0.16666666666666666),
        ('76', 0.16666666666666666),
        ('212', 0.16666666666666666)
    ]
    '''
    holder = []
    for key, val in counter.most_common():
        holder.append((key, val/lng))
    if verbose:
        for key, val in holder:
            print('key: {: >4s} - {: >5.2f}%'. format(key, val))
    return holder

#################
#A set of functions for arcticle extractions and law names analysis
def convert_list_of_strings_to_list_of_tokens(list_of_strings):
    return [item.lower().split(' ') for item in list_of_strings]
    
def extract_arts(list_of_l_tokens, test_set):
    '''
    Exctracts numbers of law articles from list of tokens:
        ['some', 'text', '123', 'civil', 'code']
        return: '123 civil code'
    Also do some simple statistical calculations
    '''
    res = []
    for row in list_of_l_tokens:
        for ind, _ in enumerate(row):
            token = row[ind]
            if token in test_set and ind > 0:
                res.append(row[ind-1])
    count_res = Counter(res)
    percents = collect_art_dispers(count_res, len(res))
    return count_res, res, percents

def extract_arts_main(list_of_strings, test_set):
    '''
    Main function in the set
    '''
    list_of_lists = convert_list_of_strings_to_list_of_tokens(list_of_strings)
    count_res, res, percents = extract_arts(list_of_lists, test_set)
    return count_res, res, percents
######
def extract_new_laws(list_of_l_tokens, test_set):
    '''
    Variation of the 'extract_arts' function. This function
    extracts some text information (in particulary, law names)
    which occures after article number:
        ['some', 'text', '123', 'civil', 'code']
        return: 'civil code'
    '''
    res = []
    for row in list_of_l_tokens:
        for ind, _ in enumerate(row):
            token = row[ind]
            if token in test_set and ind > 0:
                res.append(' '.join(row[ind:]))
                break
    #count_res = Counter(res)
    #percents = collect_art_dispers(count_res, len(res))
    return res #count_res, res, percents

def extract_new_laws_main(list_of_strings, test_set):
    '''
    Main function in this subdomain
    '''
    list_of_lists = convert_list_of_strings_to_list_of_tokens(list_of_strings)
    res = extract_new_laws(list_of_lists, test_set)
    return res
#################

def docs_writer(nums, doc_keeper):
    '''
    Write documents from doc_keeper (iop_object of corpus iterator)
    to .txt files. File names are created in respect to document numbers
    '''
    for num in nums:
        writer(doc_keeper(num), 'test_{}'.format(num), mode='w')

#################

def list_of_lists_2_list_of_strings(list_of_lists):
    return [string for column in list_of_lists for string in column]

def create_lem_map_for_list_of_strings(list_of_strings, parser):
    long_string = ' '.join(list_of_strings)
    tokens = set(re.findall(r'[А-я0-9n\-]+', long_string))
    lem_map = {token:parser(token).normal_form for token in tokens}
    return lem_map

def normalize_strings_in_lists_of_strings(list_of_strings, lem_map):
    list_of_lists_of_tokens = [
        re.findall(r'[А-я0-9n\-]+', raw_str) for raw_str in list_of_strings
    ]
    list_of_lists_of_lemms = [
        [lem_map[token] for token in lst] for lst in list_of_lists_of_tokens
    ]
    list_of_lem_strings = [' '.join(row) for row in list_of_lists_of_lemms]
    return list_of_lem_strings

def main_normalize_strings_in_lists(list_of_lists, parser):
    print('start')
    list_of_strings = list_of_lists_2_list_of_strings(list_of_lists)
    print('\tcreated list_of_strings, length:', len(list_of_strings))
    lem_map = create_lem_map_for_list_of_strings(list_of_strings, parser)
    print('\tcreated lem_map, length:', len(lem_map))
    return normalize_strings_in_lists_of_strings(list_of_strings, lem_map)


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