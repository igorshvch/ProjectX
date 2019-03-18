import logging
import time
import pathlib

import gensim as gsm
from tempscripts import (
    iotext as iot,
    textproctool as tpt
)
from textproc import PARSER
from guidialogs import ffp, fdp
from debugger import timer_with_func_name

logging.basicConfig(
    format='{asctime} : {levelname} : {message}',
    style='{', level=logging.INFO
)

#Preliminaries
#   corpus_iterator - 'iot.MyReaderPre' object
#   dct - 'gensim.corpora.Dictionary' object, corresponds to bag-of-words model
#   pkl - 'tpt.IOPickler' object connected to file with stored BOW VSM
#   tfidf - 'gensim.models.TfidfModel' object
#   pkl_tfidf - 'tpt.IOPickler' object connected to file with stored TFIDF VSM

def define_globs():
    global WORK_DIRECTORY
    global TODAY
    WORK_DIRECTORY = pathlib.Path(fdp())
    TODAY = time.strftime('%Y-%m-%d')

define_globs()

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
def create_dct(file,
               stpw,
               no_below,
               no_above,
               doc_delimiter=r'-{66}',
               mode='raw'):
    '''
    Create gensim.corpora.Dictionary object and iot.MyReaderPre object
    '''
    corpus_iterator = iot.MyReaderPre(file)
    corpus_iterator.find_docs(doc_delimiter)
    if mode == 'raw':
        tknz = iot.Tokenizer(corpus_iterator)
    elif mode == 'lem':
        tknz = iot.TokenizerLem(corpus_iterator)
    elif mode == 'bgr':
        tknz = iot.TokenizerLemBigr(corpus_iterator)
    else:
        return 'Unknown "mode" key word arg'
    dct = gsm.corpora.Dictionary(tknz, prune_at=4000000)
    stpw_ids = dct.doc2idx(stpw)
    dct.filter_tokens(bad_ids=stpw_ids)
    dct.filter_extremes(no_below=no_below, no_above=no_above, keep_n=None)
    dct.compactify()
    return dct, corpus_iterator, tknz

@timer_with_func_name
def save_vsm_model_on_disk(dct, tokenizer, ending='pkl_bow'):
    '''
    Create tpt.IOPickler object, connected to file with BOW VSM
    '''
    file_name = create_path(ending)
    file_pkl = open(file_name, mode='w+b')
    pkl = tpt.IOPickler(file_pkl)
    pkl.write(dct.doc2bow(doc) for doc in tokenizer)
    return pkl

@timer_with_func_name
def transform_to_tfidf_and_save_vsm_on_disk(pkl, ending='pkl_tfidf'):
    '''
    Create gensim.models.TfidfModel object and tpt.IOPickler
    connected to file with TFIDF VSM
    '''
    file_name = create_path(ending)
    file_pkl = open(file_name, mode='w+b')
    tfidf = gsm.models.TfidfModel(pkl.load_all_items())
    pkl_tfidf = tpt.IOPickler(file_pkl)
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
def find_key_words(num_kwords, tokens_vector, dct):
    '''
    Find num_kwords key words from vector.
    Vector must be an gensim.models.TfidfModel()[gensim.corpora.Dictionary().doc2bow(list_of_tokens)]
    '''
    top_tokens = sorted(
        tokens_vector, key=lambda x: x[1], reverse=True
    )[:num_kwords]
    head = '{: >4s}     {: >40s}     {: >5s}     {: >8s}'.format('ID', 'KEY', 'WID', 'SCORE')
    print(head)
    print('-'*len(head))
    for idn, pair in enumerate(top_tokens, start=1):
        token, score = pair
        for key, val in dct.token2id.items():
            if val == token:
                print(
                    '{: >4d}     {: >40s}     {: >5d}     {: >8.6f}'.format(idn, key,val,score)
                )
                break

##################################
##From console for refactoring ###
##################################

def create_inverted_index(corpus_iterator):
    '''
    Unefficient function for creating inverted index table
    '''
    iid = {}
    tknz = iot.Tokenizer(corpus_iterator)
    for ind, tokens_doc in enumerate(tknz):
        if ind % 10000 == 0:
            print(ind)
        tokens_set = set(tokens_doc)
        for token in tokens_set:
            iid.setdefault(token, []).append(ind)
    return iid

def find_req(corpus_iterator, index):
    '''
    Return:
    ФЕДЕРАЛЬНЫЙ АРБИТРАЖНЫЙ СУД ВОЛГО-ВЯТСКОГО ОКРУГА от 3 июля 2013 г. по делу N А43-34943/2011
    '''
    act = corpus_iterator.find_doc(index).split('\n')
    return act[1].strip('\n\r') + ' ' + act[4].strip('\n\r')

def print_sims(corpus_iterator, sims):
    '''
    Print:
    01 >>>    ФЕДЕРАЛЬНЫЙ АРБИТРАЖНЫЙ СУД ВОЛГО-ВЯТСКОГО ОКРУГА от 3 июля 2013 г. по делу N А43-34943/2011 >>> 0.27
    02 >>>  ФЕДЕРАЛЬНЫЙ АРБИТРАЖНЫЙ СУД ВОЛГО-ВЯТСКОГО ОКРУГА от 6 февраля 2012 г. по делу N А28-6861/2011 >>> 0.26
    03 >>>      ФЕДЕРАЛЬНЫЙ АРБИТРАЖНЫЙ СУД ВОЛГО-ВЯТСКОГО ОКРУГА арбитражного суда кассационной инстанции >>> 0.22
    '''
    for index, item in enumerate(sims, start=1):
        print('{:0>2d} >>> {: <110s} - {: >5d} - {: >4.2f}'.format(index, find_req(corpus_iterator, item[0]), item[0], item[1]))

def find_relevant_docs(iid, q_words):
    '''
    Find docs with query words
    Return:
    [intersection_result_1, intersection_result_2, intersection_result3...]
    '''
    all_docs = [set(iid[word]) for word in q_words]
    res = [all_docs[0].intersection(*all_docs[0:i]) for i in range(1, len(all_docs))]
    return res

class QueryProcessor():
    def __init__(self, query_full, query_short, word_len):
        self.query = {'raw': query_full}
        self.query_short = {'raw': query_short}
        self.tokenize()
        self.lemmatize()
        self.create_bigrams(word_len=word_len)
    
    def tokenize(self):
        self.query['tok'] = [
            word.strip('!"#$%&\'()*+,./:;<=>?@[\\]^_`{|}~')
            for word in self.query['raw'].lower().split(' ')
        ]
        self.query_short['tok'] = [
            word.strip('!"#$%&\'()*+,./:;<=>?@[\\]^_`{|}~')
            for word in self.query_short['raw'].lower().split(' ')
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