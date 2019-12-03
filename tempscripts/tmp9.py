import re
import random
import math
from collections import Counter

import debugger as dbg
from writer import writer

ART_SUB_SHORTHANDS = {
    'пункт': 'п',
    'подпункт': 'п',
    'п.': 'п',
    'пп.': 'п',
    'п.п.': 'п',
    'часть': 'ч',
    'ч.': 'ч',
    'чч.': 'ч',
    'ч.ч.': 'ч',
    'статья': 'ст',
    'ст': 'ст',
    'ст.': 'ст',
    'ст.ст.': 'ст'
}

LITERAL_TO_NUMERAL_BELOW = {
    'пер': '1',
    'вто': '2',
    'тре': '3',
    'оди': '1',
    'два': '2',
    'три': '3',
    'чет': '4',
    'пят': '5',
    'шес': '6',
    'сем': '7',
    'вос': '8',
    'дев': '9',
    'дес': '10'
}
LITERAL_TO_NUMERAL_ABOVE = {
    'оди': '11',
    'две': '12',
    'три': '13',
    'чет': '14',
    'пят': '15',
    'шес': '16',
    'сем': '17',
    'вос': '18',
    'дев': '19',
    'два': '20'
}

LITERAL_TO_NUMERAL = {
    'один': '1',
    'два': '2',
    'три': '3',
    'четыре': '4',
    'пять': '5',
    'шесть': '6',
    'семь': '7',
    'восемь': '8',
    'девять': '9',
    'десять': '10',
    'одиннадцать': '11',
    'двенадцать': '12',
    'треть': '3',
    'четвертовать': '4',
}


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
    ########
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
    ########
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
            print(
                '\t', 'doc#', iind, 'time:', '{: >6.2f}'.format(
                    dbg.time()-time
                    )
            )
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

def collect_art_dispers(counter, arts_in_total, verbose=False):
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
        holder.append((key, val/arts_in_total))
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

def extract_arts_compaund(list_of_strings, test_set):
    list_of_lists = convert_list_of_strings_to_list_of_tokens(list_of_strings)
    count_res, res, percents = extract_arts(list_of_lists, test_set)
    return count_res, res, percents

def main_extract_arts(art_mapping, test_set):
    '''
    Main function in this area
    art_mapping - iterable object with lists_of_strings
    test_set - set object with words describing laws
    test_set contains derivatives from following words:
    тк трудовой
    '''
    holder = []
    for ind, mapping in enumerate(art_mapping):
        if ind % 3000 == 0:
            print('mapping for doc#', ind)
        holder.append(extract_arts_compaund(mapping, test_set))
    return holder
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

def extract_new_laws_compaund(list_of_strings, test_set):
    list_of_lists = convert_list_of_strings_to_list_of_tokens(list_of_strings)
    res = extract_new_laws(list_of_lists, test_set)
    return res

def main_extract_new_laws(art_mapping, test_set):
    '''
    Main function in this subdomain
    art_mapping - iterable object with lists_of_strings
    test_set - set object with words describing laws
    test_set contains derivatives from following words:
    ук апк упк гражданский жилищный
    гк тк уголовный уголовно коап кодекс
    арбитражный закон трудовой гпк
    земельный федеральный
    '''
    holder = []
    for ind, mapping in enumerate(art_mapping):
        if ind % 3000 == 0:
            print('mapping for doc#', ind)
        holder.append(extract_new_laws_compaund(mapping, test_set))
    return holder
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

def create_lem_map_for_list_of_strings(
                                       list_of_strings,
                                       parser,
                                       pattern=r'[А-я0-9n\-]+'
                                      ):
    long_string = ' '.join(list_of_strings)
    tokens = set(re.findall(pattern, long_string))
    lem_map = {token:parser(token).normal_form for token in tokens}
    return lem_map

def normalize_strings_in_lists_of_strings(
                                          list_of_strings,
                                          lem_map,
                                          pattern=r'[А-я0-9n\-]+'
                                         ):
    list_of_lists_of_tokens = [
        re.findall(pattern, raw_str) for raw_str in list_of_strings
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
    list_of_lem_strings = normalize_strings_in_lists_of_strings(
        list_of_strings, lem_map
    )
    print('\tcreated list_of_lem_strings, length:', len(list_of_lem_strings))
    return list_of_lem_strings

def list_of_lem_strings_count_adn_pretty(list_of_lem_strings):
    '''
    Return:
    [
        кодекс российский федерация                        :  70017
        гражданский процессуальный кодекс российский       :  36396
        кодекс российский федерация о                      :  16712
    ],
    'Counter' object
    '''
    cnt = Counter(list_of_lem_strings)
    pretty_strings = [
        '{: <55s} : {: >6d}'.format(item[0], item[1])
        for item in cnt.most_common()
    ]
    return pretty_strings, cnt
######
def normalize_strings_in_list_of_lists(list_of_lists, lem_map):
    list_of_lists_lemmed = []
    list_for_set = []
    uniq_strings = set()
    for lst in list_of_lists:
        inner_res_list = []
        for raw_string in lst:
            inner_token_lst = re.findall(r'[А-я0-9n\-]+', raw_string)
            inner_lem_lst = [lem_map[token] for token in inner_token_lst]
            lem_string = ' '.join(inner_lem_lst)
            inner_res_list.append(lem_string)
        list_of_lists_lemmed.append(inner_res_list)
        list_for_set.extend(inner_res_list)
    uniq_strings = set(list_for_set)
    return list_of_lists_lemmed, uniq_strings

def eval_doc_freq(list_of_lists_lemmed, uniq_strings):
    df_collector = {lem_string:0 for lem_string in uniq_strings}
    for list_lemmed in list_of_lists_lemmed:
        for lem_string in set(list_lemmed):
            df_collector[lem_string] += 1
    return df_collector

def count_idf(df_collector, collection_length):
    idf_collector = {}
    for lem_string in df_collector:
        idf_collector[lem_string] = math.log10(
            collection_length/df_collector[lem_string]
        )
    return idf_collector

def main_idf_eval(list_of_lists, parser):
    print('start')
    list_of_strings = list_of_lists_2_list_of_strings(list_of_lists)
    print('\tcreated list_of_strings, length:', len(list_of_strings))
    lem_map = create_lem_map_for_list_of_strings(list_of_strings, parser)
    print('\tcreated lem_map, length:', len(lem_map))
    list_of_lists_lemmed, uniq_strings = normalize_strings_in_list_of_lists(
        list_of_lists, lem_map
    )
    print(
        '\tcreated list_of_lists_lemmed and uniq_strings, length:',
        len(list_of_lists_lemmed), 'and', len(uniq_strings)
    )
    df_collector = eval_doc_freq(list_of_lists_lemmed, uniq_strings)
    print('\tcreated df_collector, length:', len(df_collector))
    idf_collector = count_idf(df_collector, len(list_of_lists))
    print('\tcreated idf_collector, length:', len(idf_collector))
    return df_collector, idf_collector

############

def convert_raw_tokens_to_lemms(
                                iop1,
                                iop2,
                                lem_map,
                                pattern=r'[А-я0-9n\-.]+'
                               ):
    '''
    Perform convertion betwween two iop.IOPickler()-objects
    contains of lists_of_strings in accrodance with the following
    procedure:
    1) from each list take each string
    2) find all tokens according to the pattern
    3) normalize tokens by lem_map dictionary
    4) append list of normed tokens to the intermediate holder
    5) append intermidiate holder to iop2
    '''
    internal_list = []
    for ind, lst in enumerate(iop1):
        if ind % 5000 == 0:
            print('doc #', ind)
        for string in lst:
            spl_str = re.findall(pattern, string)
            spl_str = [lem_map[token] for token in spl_str]
            internal_list.append(spl_str)
        iop2.append(internal_list)
        internal_list = []



def test_search_func(
                     test_list_of_strings,
                     shd=ART_SUB_SHORTHANDS,
                     l2n=LITERAL_TO_NUMERAL,
                     concatenate=False
                     #lnb = LITERAL_TO_NUMERAL_BELOW,
                     #lna = LITERAL_TO_NUMERAL_ABOVE
                    ):
    holder = []
    #errors = []
    SUB_SUB_ART_SH = {'пункт', 'подпункт', 'п.', 'пп.', 'п.п.'}
    SUB_ART_SH = {'часть', 'ч.', 'чч.', 'ч.ч.'}
    ARTICLE_SHORTHANDS = {'статья', 'ст', 'ст.', 'ст.ст.'}
    for ind, tokens_list in enumerate(test_list_of_strings):
        ih = [] # intermidiate holder
        while tokens_list:
            token = tokens_list.pop(0)
            if token in SUB_SUB_ART_SH:
                #print(ind, 'level1', token, end=' /// ')
                ih.append(shd[token])
                try:
                    num = tokens_list.pop(0)
                except:
                    ih = []
                    break
                if num.isalpha():
                    ih.append(l2n[num] if num in l2n else '#')
                else:
                    ih.append(num)
                #if num.isalpha():
                #    errors.append(num)
                ih.append(num)
                continue
            if token in SUB_ART_SH:
                #print(ind, 'level2', token, end=' /// ')
                ih.append(shd[token])
                try:
                    num = tokens_list.pop(0)
                except:
                    ih = []
                    break
                if num.isalpha():
                    ih.append(l2n[num] if num in l2n else '#')
                else:
                    ih.append(num)
                #if num.isalpha():
                #    errors.append(num)
                continue
            if token in ARTICLE_SHORTHANDS:
                #print(ind, 'level3', token, end=' /// ')
                ih.append(shd[token])
                try:
                    num = tokens_list.pop(0)
                except:
                    ih = []
                    break
                if num.isalpha():
                    if num in l2n:              ####
                        ih.append(num)          ####
                    else:                       ####
                        tokens_list = False     ####
                        ih = []                 ####
                        break                   ####
                else:
                    ih.append(num)
                #if num.isalpha():
                #    errors.append(num)
                #ih.append(num)
                try:
                    new_token = tokens_list.pop(0)
                except:
                    ih = []
                    break
                if new_token in {'гпк', 'коап', 'тк'}:
                    #print(ind, 'level3.1', new_token, end=' /// ')
                    ih.append(new_token)
                else:
                    #print(ind, 'level3.2', new_token, end=' /// ')
                    if new_token == 'гражданский':
                        try:
                            another_new_token = tokens_list.pop(0)
                        except:
                            ih = []
                            break                        
                        if another_new_token == 'процессуальный':
                            #print(ind, 'level3.2.1', another_new_token, end=' /// ')
                            ih.append('гпк')
                    elif new_token == 'кодекс':
                        try:
                            another_new_token = tokens_list.pop(0)
                        except:
                            ih = []
                            break
                        if another_new_token == 'российский':
                            #print(ind, 'level3.2.1', another_new_token, end=' /// ')
                            ih.append('коап')
                    elif new_token == 'трудовой':
                        #print(ind, 'level3.2.3', new_token, end=' /// ')
                        ih.append('тк')
                    else:
                        #print(ind, 'LEVEL3.2.4', new_token, end=' /// ')
                        ih = []
                        break
        if concatenate: 
            res = ' '.join(ih[::-1])
        #print(res, bool(res))
        else:
            res = ih[::-1]
        holder.append(res)
    return sorted([item for item in holder if item]) #, errors


#' '.join(test_set2)
#Out[607]: 'арбитражной уголовная тк земельной законом закону уголовного арбитражно арбитражный жилищном жилищною законе арбитражному упк гражданскому жилищный уголовною коап уголовен кодекса земельна кодексом гражданским жилищной земельном кодексе земельным арбитражную арбитражное уголовный трудовую земелен жилищному арбитражною гражданской уголовную земельною арбитражен уголовной гк жилищно гражданскую трудовою земельно гражданское федеральном федерально жилищным земельную арбитражна гражданская федеральному трудовое федеральной уголовном уголовным земельное федеральною закона трудовая закон трудовой федеральное гражданский земельная жилищная арбитражного трудовым федеральную арбитражном федеральный апк жилищна федеральна федерального гпк арбитражным земельного жилищен гражданского федеральная уголовна трудовом кодексу жилищную гражданском земельному трудового кодекс гражданскою федеральным федерален жилищного арбитражная ук уголовному трудовому уголовно жилищное уголовное земельный'

#' '.join(test_set3)
#Out[608]: 'арбитражной уголовная тк земельной законом закону уголовного арбитражно арбитражный жилищном жилищною законе арбитражному упк гражданскому жилищный уголовною коап уголовен земельна гражданским жилищной земельном земельным арбитражную арбитражное уголовный земелен жилищному арбитражною гражданской уголовную земельною арбитражен уголовной гк жилищно гражданскую земельно гражданское федеральном федерально жилищным земельную арбитражна гражданская федеральному федеральной уголовном уголовным земельное федеральною закона закон федеральное гражданский земельная жилищная арбитражного федеральную арбитражном федеральный апк жилищна федеральна федерального гпк арбитражным земельного жилищен гражданского федеральная уголовна жилищную гражданском земельному гражданскою федеральным федерален жилищного арбитражная ук уголовному уголовно жилищное уголовное земельный'

#for ind, doc_map_raw in enumerate(iop_obj_lemmed):
#    if ind % 5000 == 0:
#        print('doc#', ind)
#    doc_map = tmp.test_search_func(doc_map_raw)
#    iop_obj_maps.append(doc_map)

#for ind, doc in enumerate(iop_obj_maps):
#    if ind % 5000 == 0:
#        print('doc#', ind)
#    ihr = []
#    for lst in doc:                    for lst in doc:
#        c, norm = lst[0], lst[1]           c, norm = lst[0], lst[1]
#        ihr.append(c+'_'+norm)             if c != 'гпк':
#    inter_maps.append(ihr)                     ihr.append(c+'_'+norm)
#                                       if ihr:
#                                           inter_maps.append(ihr)



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
