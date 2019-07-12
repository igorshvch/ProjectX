import logging
import time
import pathlib

import gensim as gsm

from atctds_search_civil import (
    tokenizer as tok,
    iopickler as iop,
    debugger as dbg
)
from atctds_search_civil.textproc import rwtools, PARSER

logging.basicConfig(
    format='{asctime} : {levelname} : {message}',
    style='{', level=logging.INFO
)










from atctds_search_civil.guidialogs import ffp, fdp
from atctds_search_civil.debugger import timer_with_func_name


def define_globs():
    global WORK_DIRECTORY
    global TODAY
    WORK_DIRECTORY = pathlib.Path(fdp())
    TODAY = time.strftime('%Y-%m-%d')

#Preliminaries
#   corpus_iterator - 'iot.MyReaderPre'/'iot.MyReaderEndDate'
#                      or 'iot.TextInfoCollectorPre'  object
#   dct - 'gensim.corpora.Dictionary' object
#         corresponds to bag-of-words (BOW) model
#   pkl - 'iop.IOPickler' object connected
#         to file with stored BOW vector space model (VSM)
#   tfidf - 'gensim.models.TfidfModel' object
#   pkl_tfidf - 'iop.IOPickler' object connected to file with stored TFIDF VSM


def create_path(ending):
    today_ending = TODAY+'_'+ending
    fp = pathlib.Path(WORK_DIRECTORY).joinpath(today_ending)
    counter = 1
    while True:
        if fp.exists():
            fp = pathlib.Path(WORK_DIRECTORY).joinpath(
                today_ending+'{:0>3d}'.format(counter)
            )
            counter += 1
        else:
            break
    return fp

@timer_with_func_name
def create_dct(corpus_iterator,
               stpw,
               no_below,
               no_above,
               mode='tok',
               lem_map=None,
               word_len=1):
    '''
    Create gensim.corpora.Dictionary object and iot.MyReaderPre object
    '''
    if mode == 'tok':
        tknz = tok.Tokenizer(corpus_iterator, stpw)
    elif mode == 'lem':
        tknz = tok.TokenizerLem(corpus_iterator, stpw, lem_map=lem_map)
    elif mode == 'bgr':
        tknz = tok.TokenizerLemBigr(
            corpus_iterator,
             stpw,
             word_len=word_len,
             lem_map=lem_map
        )
    elif mode == 'tgr':
        tknz = tok.TokenizerLemTrigr(
            corpus_iterator,
            stpw,
            word_len=word_len,
            lem_map=lem_map
        )
    else:
        raise ValueError('Unknown "mode" keyword arg')
    dct = gsm.corpora.Dictionary(tknz, prune_at=4000000)
    stpw_ids = dct.doc2idx(stpw)
    dct.filter_tokens(bad_ids=stpw_ids)
    dct.filter_extremes(no_below=no_below, no_above=no_above, keep_n=None)
    dct.compactify()
    return dct, tknz

@timer_with_func_name
def save_vsm_model_on_disk(dct, tokenizer, ending='pkl_bow'):
    '''
    Create iop.IOPickler object, connected to file with BOW VSM
    '''
    file_name = create_path(ending)
    file_pkl = open(file_name, mode='w+b')
    pkl = iop.IOPickler(file_pkl)
    pkl.write(dct.doc2bow(doc) for doc in tokenizer)
    return pkl

@timer_with_func_name
def transform_to_tfidf_and_save_vsm_on_disk(pkl, ending='pkl_tfidf'):
    '''
    Create gensim.models.TfidfModel object and iop.IOPickler
    connected to file with TFIDF VSM
    '''
    file_name = create_path(ending)
    file_pkl = open(file_name, mode='w+b')
    tfidf = gsm.models.TfidfModel(pkl.load_all_items())
    pkl_tfidf = iop.IOPickler(file_pkl)
    pkl_tfidf.write(tfidf[doc] for doc in pkl.load_all_items())
    return tfidf, pkl_tfidf

@timer_with_func_name
def create_similarity_object(pkl_tfidf, dct, num_best):
    index_sim = gsm.similarities.Similarity(
        None,
        pkl_tfidf.load_all_items(),
        num_features=len(dct),
        num_best=num_best
    )
    return index_sim

@timer_with_func_name
def find_key_words(num_kwords, tokens_vector, dct, file=None):
    '''
    Find num_kwords key words from vector.
    Vector must be a gensim.models.TfidfModel()[gensim.corpora.Dictionary().doc2bow(list_of_tokens)]
    '''
    top_tokens = sorted(
        tokens_vector, key=lambda x: x[1], reverse=True
    )[:num_kwords]
    head = '{: >4s}     {: >40s}     {: >7s}     {: >8s}'.format('ID', 'KEY', 'WID', 'SCORE')
    print(head)
    print('-'*len(head))
    for idn, pair in enumerate(top_tokens, start=1):
        token, score = pair
        for key, val in dct.token2id.items():
            if val == token:
                st = '{: >4d}     {: >40s}     {: >7d}     {: >8.6f}'.format(
                    idn, key, val, score
                )
                if file:
                    file.write(st+'\n')
                else:
                    print(st)
                break

@timer_with_func_name
def create_four_models(corpus_iterator, stpw, pars, num_best=10, word_len=3):
    modes = 'tok', 'lem', 'bgr', 'tgr'
    dct = {mode:{} for mode in modes}
    for mode in 'tok', 'lem':
        dct[mode]['dct'], dct[mode]['tknz'] = create_dct(
            corpus_iterator, stpw, pars[0], pars[2], mode=mode
        )
    for mode in 'bgr', 'tgr':
        dct[mode]['dct'], dct[mode]['tknz'] = create_dct(
            corpus_iterator,
            stpw,
            pars[1],
            pars[3],
            mode=mode,
            lem_map=dct['lem']['tknz'].lem_map,
            word_len=word_len
        )
    for mode in modes:
        dct[mode]['pkl_bow'] = save_vsm_model_on_disk(
            dct[mode]['dct'],
            dct[mode]['tknz'],
            ending='pkl_bow_'+mode
        )
        dct[mode]['tfidf'], dct[mode]['pkl_tfidf'] = (
            transform_to_tfidf_and_save_vsm_on_disk(
                dct[mode]['pkl_bow'],
                ending='pkl_tfidf_'+mode
            )
        )
        dct[mode]['index_sim'] = create_similarity_object(
            dct[mode]['pkl_tfidf'],
            dct[mode]['dct'],
            num_best
        )
    return dct

@timer_with_func_name
def create_three_models(corpus_iterator, stpw, pars, num_best=10, word_len=3):
    modes = 'lem', 'bgr', 'tgr'
    dct = {mode:{} for mode in modes}
    dct['lem']['dct'], dct['lem']['tknz'] = create_dct(
        corpus_iterator, stpw, pars[0], pars[2], mode='lem'
    )
    for mode in 'bgr', 'tgr':
        dct[mode]['dct'], dct[mode]['tknz'] = create_dct(
            corpus_iterator,
            stpw,
            pars[1],
            pars[3],
            mode=mode,
            lem_map=dct['lem']['tknz'].lem_map,
            word_len=3
        )
    for mode in modes:
        dct[mode]['pkl_bow'] = save_vsm_model_on_disk(
            dct[mode]['dct'],
            dct[mode]['tknz'],
            ending='pkl_bow_'+mode
        )
        dct[mode]['tfidf'], dct[mode]['pkl_tfidf'] = (
            transform_to_tfidf_and_save_vsm_on_disk(
                dct[mode]['pkl_bow'],
                ending='pkl_tfidf_'+mode
            )
        )
        dct[mode]['index_sim'] = create_similarity_object(
            dct[mode]['pkl_tfidf'],
            dct[mode]['dct'],
            num_best
        )
    return dct

@timer_with_func_name
def create_two_models1(corpus_iterator, stpw, pars, num_best=10, word_len=3):
    modes = 'lem', 'bgr'
    dct = {mode:{} for mode in modes}
    dct['lem']['dct'], dct['lem']['tknz'] = create_dct(
        corpus_iterator, stpw, pars[0], pars[2], mode='lem'
    )
    dct['bgr']['dct'], dct['bgr']['tknz'] = create_dct(
        corpus_iterator,
        stpw,
        pars[1],
        pars[3],
        mode='bgr',
        lem_map=dct['lem']['tknz'].lem_map,
        word_len=word_len
    )
    for mode in modes:
        dct[mode]['pkl_bow'] = save_vsm_model_on_disk(
            dct[mode]['dct'],
            dct[mode]['tknz'],
            ending='pkl_bow_'+mode
        )
        dct[mode]['tfidf'], dct[mode]['pkl_tfidf'] = (
            transform_to_tfidf_and_save_vsm_on_disk(
                dct[mode]['pkl_bow'],
                ending='pkl_tfidf_'+mode
            )
        )
        dct[mode]['index_sim'] = create_similarity_object(
            dct[mode]['pkl_tfidf'],
            dct[mode]['dct'],
            num_best
        )
    return dct

@timer_with_func_name
def create_two_models2(corpus_iterator, stpw, pars, num_best=10, word_len=3):
    modes = 'bgr', 'tgr'
    dct = {mode:{} for mode in modes}
    dct['bgr']['dct'], dct['bgr']['tknz'] = create_dct(
        corpus_iterator, stpw, pars[0], pars[2], mode='bgr', word_len=word_len
    )
    dct['tgr']['dct'], dct['tgr']['tknz'] = create_dct(
        corpus_iterator,
        stpw,
        pars[1],
        pars[3],
        mode='tgr',
        lem_map=dct['bgr']['tknz'].lem_map,
        word_len=word_len
    )
    for mode in modes:
        dct[mode]['pkl_bow'] = save_vsm_model_on_disk(
            dct[mode]['dct'],
            dct[mode]['tknz'],
            ending='pkl_bow_'+mode
        )
        dct[mode]['tfidf'], dct[mode]['pkl_tfidf'] = (
            transform_to_tfidf_and_save_vsm_on_disk(
                dct[mode]['pkl_bow'],
                ending='pkl_tfidf_'+mode
            )
        )
        dct[mode]['index_sim'] = create_similarity_object(
            dct[mode]['pkl_tfidf'],
            dct[mode]['dct'],
            num_best
        )
    return dct

@timer_with_func_name
def create_one_model(corpus_iterator, stpw, pars, num_best=15, mode='bgr', word_len=3):
    dct = {mode:{}}
    dct[mode]['dct'], dct[mode]['tknz'] = create_dct(
        corpus_iterator, stpw, pars[0], pars[1], mode=mode, word_len=word_len
    )
    dct[mode]['pkl_bow'] = save_vsm_model_on_disk(
        dct[mode]['dct'],
        dct[mode]['tknz'],
        ending='pkl_bow_'+mode
    )
    dct[mode]['tfidf'], dct[mode]['pkl_tfidf'] = (
        transform_to_tfidf_and_save_vsm_on_disk(
            dct[mode]['pkl_bow'],
            ending='pkl_tfidf_'+mode
        )
    )
    dct[mode]['index_sim'] = create_similarity_object(
        dct[mode]['pkl_tfidf'],
        dct[mode]['dct'],
        num_best
    )
    return dct

class QueryProcessor():
    def __init__(self, query_full, query_short, stpw, word_len=1):
        self.query = {'raw': query_full}
        self.query_short = {'raw': query_short}
        self.tokenize(stpw)
        self.lemmatize()
        self.create_bigrams(word_len=word_len)
        self.create_trigrmas(word_len=word_len)
    
    def tokenize(self, stpw):
        self.query['tok'] = [
            word.strip('!"#$%&\'()*+,./:;<=>?@[\\]^_`{|}~')
            for word in self.query['raw'].lower().split(' ')
            if word not in stpw
        ]
        self.query_short['tok'] = [
            word.strip('!"#$%&\'()*+,./:;<=>?@[\\]^_`{|}~')
            for word in self.query_short['raw'].lower().split(' ')
            if word not in stpw
        ]
    
    def lemmatize(self):
        self.query['lem'] = [PARSER(word) for word in self.query['tok']]
        self.query_short['lem'] = [
            PARSER(word) for word in self.query_short['tok']
        ]
    
    def create_bigrams(self, word_len=1):
        query = [
            word for word in self.query['lem'] if len(word)>word_len
        ]
        query_short = [
            word for word in self.query_short['lem'] if len(word)>word_len
        ]
        self.query['bgr'] = [
            query[i-1]+'#'+query[i]
            for i in range(1, len(query), 1)
        ]
        self.query_short['bgr'] = [
            query_short[i-1]+'#'+query_short[i]
            for i in range(1, len(query_short), 1)
        ]
    
    def create_trigrmas(self, word_len=1):
        query = [
            word for word in self.query['lem'] if len(word)>word_len
        ]
        query_short = [
            word for word in self.query_short['lem'] if len(word)>word_len
        ]
        self.query['tgr'] = [
            query[i-2]+'#'+query[i-1]+'#'+query[i]
            for i in range(2, len(query), 1)
        ]
        self.query_short['tgr'] = [
            query_short[i-2]+'#'+query_short[i-1]+'#'+query_short[i]
            for i in range(2, len(query_short), 1)
        ]
    
def form_one_output(models, q_proc, q_len='full'):
    '''
    models - 'dict' object with priveously created gensim models
    q_proc - local var for 'QueryProcessor' object
    q_len - flag to chose query type from 'QueryProccesor' object: full or short
    
    Return:
    [
        (6727, 0.3714553117752075, 'bgrlemtok'),
        (7563, 0.3039359599351883, 'lemtok'),
        ...        
    ]
    '''
    modes_models = sorted(models.keys())
    sims = {mode:None for mode in modes_models}
    if q_len == 'full':
        query = q_proc.query
    elif q_len == 'short':
        query = q_proc.query_short
    else:
        raise ValueError('Incorrect q_len keyword argument!')
    for mode in modes_models:
        sims[mode] = models[mode]['index_sim'][
            models[mode]['tfidf'][
                models[mode]['dct'].doc2bow(
                    query[mode]
                )
            ]
        ]
    holder1 = []
    for mode in modes_models:
        for ind, scr in sims[mode]:
            holder1.append((ind, scr, mode))
    holder2 = {
        ind: {'scr': 0, 'mode': ''} for ind, _, _ in holder1
    }
    for item in holder1:
        holder2[item[0]]['scr']+=item[1]
        holder2[item[0]]['mode']+=item[2]
    res = [(key, holder2[key]['scr'], holder2[key]['mode']) for key in holder2]
    res = sorted(res, key=lambda x: x[1], reverse=True)
    return res

def form_one_output_with_amendments(models,
                                    q_proc,
                                    q_len='full',
                                    amend_mode='bgr',
                                    amend=0.7):
    '''
    models - 'dict' object with priveously created gensim models
    q_proc - local var for 'QueryProcessor' object
    q_len - flag to chose query type from 'QueryProccesor' object: full or short
    amend - amount by which score value increases
    
    Return:
    [
        (6727, 0.3714553117752075, 'bgrlemtok'),
        (7563, 0.3039359599351883, 'lemtok'),
        ...        
    ]
    '''
    modes_models = sorted(models.keys())
    sims = {mode:None for mode in modes_models}
    if q_len == 'full':
        query = q_proc.query
    elif q_len == 'short':
        query = q_proc.query_short
    else:
        raise ValueError('Incorrect q_len keyword argument!')
    for mode in modes_models:
        sims[mode] = models[mode]['index_sim'][
            models[mode]['tfidf'][
                models[mode]['dct'].doc2bow(
                    query[mode]
                )
            ]
        ]
    holder1 = []
    for mode in modes_models:
        for ind, scr in sims[mode]:
            if mode == amend_mode:
                scr+=amend
            holder1.append((ind, scr, mode))
    holder2 = {
        ind: {'scr': 0, 'mode': ''} for ind, _, _ in holder1
    }
    for item in holder1:
        holder2[item[0]]['scr']+=item[1]
        holder2[item[0]]['mode']+=item[2]
    res = [(key, holder2[key]['scr'], holder2[key]['mode']) for key in holder2]
    res = sorted(res, key=lambda x: x[1], reverse=True)
    return res

def find_req(corpus_iterator, index, index_var='one'):
    '''
    Return:
    ФЕДЕРАЛЬНЫЙ АРБИТРАЖНЫЙ СУД ВОЛГО-ВЯТСКОГО ОКРУГА от 3 июля 2013 г. по делу N А43-34943/2011
    '''
    if index_var == 'one':
        i = 0
        j = 3
    elif index_var == 'two':
        i = 1
        j = 4
    act = corpus_iterator[index].split('\n')
    return act[i].strip('\n\r') + ' ' + act[j].strip('\n\r')

def print_all_res(res, corpus_iterator, index_var='one', p_mode='full'):
    '''
    index_var - flag to chose proper strings with requesits in court decisions 

    Print:
    1 >>>   6727 >>> АРБИТРАЖНЫЙ СУД МОСКОВСКОГО ОКРУГА от 8 февраля 2016 г. по делу N А40-105380/15                 >>>  0.371455 >>> bgrlemraw
    2 >>>   7563 >>> АРБИТРАЖНЫЙ СУД ПОВОЛЖСКОГО ОКРУГА от 16 апреля 2018 г. N Ф06-31853/2018                        >>>  0.303936 >>>    lemraw
    3 >>>   7009 >>> АРБИТРАЖНЫЙ СУД МОСКОВСКОГО ОКРУГА от 28 сентября 2015 г. по делу N А40-208639/14               >>>  0.289477 >>> bgrlemraw
    '''
    for ind, line in enumerate(res, start=1):
        index, scr, mode = line
        req = find_req(corpus_iterator, index, index_var=index_var)
        if p_mode == 'short':
            print(req)
        elif p_mode == 'full':
            print(
                '{: >3d} >>> {: >6d} >>> {: <95s} >>> {: >9.6f} >>> {: >9s}'.format(
                ind, index, req, scr, mode)
            )



##################################
##From console for refactoring ###
##################################

def create_inverted_index(corpus_iterator, stpw):
    '''
    Unefficient function for creating inverted index table
    '''
    iid = {}
    tknz = tok.Tokenizer(corpus_iterator, stpw)
    for ind, tokens_doc in enumerate(tknz):
        if ind % 10000 == 0:
            print(ind)
        tokens_set = set(tokens_doc)
        for token in tokens_set:
            iid.setdefault(token, []).append(ind)
    return iid

@timer_with_func_name
def create_inverted_index_from_tknz(tknz):
    iid = {}
    for ind, tokened_doc in enumerate(tknz):
        if ind % 10000 == 0:
            print(ind)
        tokens_set = set(tokened_doc)
        for token in tokens_set:
            iid.setdefault(token, []).append(ind)
    return iid

def print_sims(corpus_iterator, sims):
    '''
    Print:
    01 >>>    ФЕДЕРАЛЬНЫЙ АРБИТРАЖНЫЙ СУД ВОЛГО-ВЯТСКОГО ОКРУГА от 3 июля 2013 г. по делу N А43-34943/2011 >>> 0.27
    02 >>>  ФЕДЕРАЛЬНЫЙ АРБИТРАЖНЫЙ СУД ВОЛГО-ВЯТСКОГО ОКРУГА от 6 февраля 2012 г. по делу N А28-6861/2011 >>> 0.26
    03 >>>      ФЕДЕРАЛЬНЫЙ АРБИТРАЖНЫЙ СУД ВОЛГО-ВЯТСКОГО ОКРУГА арбитражного суда кассационной инстанции >>> 0.22
    '''
    for index, item in enumerate(sims, start=1):
        print('{:0>2d} >>> {: <110s} - {: >5d} - {: >5.2f}'.format(index, find_req(corpus_iterator, item[0]), item[0], item[1]))

def find_relevant_docs(iid, q_words):
    '''
    Find docs with query words
    Return:
    [intersection_result_1, intersection_result_2, intersection_result3...]
    '''
    all_docs = [set(iid[word]) for word in q_words if word in iid]
    res = [all_docs[0].intersection(*all_docs[0:i]) for i in range(1, len(all_docs))]
    return res