import logging

import gensim as gsm
from tempscripts import (
    iotext as iot,
    textproctool as tpt
)
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

@timer_with_func_name
def create_dct(file, stpw, no_below, no_above, doc_delimiter=r'-{66}'):
    '''
    Create gensim.corpora.Dictionary object and iot.MyReaderPre object
    '''
    corpus_iterator = iot.MyReaderPre(file)
    corpus_iterator.find_docs(doc_delimiter)
    tknz = iot.Tokenizer(corpus_iterator)
    dct = gsm.corpora.Dictionary(tknz)
    stpw_ids = dct.doc2idx(stpw)
    dct.filter_tokens(bad_ids=stpw_ids)
    dct.filter_extremes(no_below=no_below, no_above=no_above, keep_n=None)
    dct.compactify()
    return dct, corpus_iterator

@timer_with_func_name
def save_vsm_model_on_disk(file_pkl_1, corpus_iterator, dct):
    '''
    Create tpt.IOPickler object, connected to file with BOW VSM
    '''
    pkl = tpt.IOPickler(file_pkl_1)
    pkl.write(dct.doc2bow(doc) for doc in iot.Tokenizer(corpus_iterator))
    return pkl

@timer_with_func_name
def transform_to_tfidf_and_save_vsm_on_disk(file_pkl_2, pkl):
    '''
    Create gensim.models.TfidfModel object and tpt.IOPickler
    connected to file with TFIDF VSM
    '''
    tfidf = gsm.models.TfidfModel(pkl.load_all_items())
    pkl_tfidf = tpt.IOPickler(file_pkl_2)
    pkl_tfidf.write(tfidf[doc] for doc in pkl.load_all_items())
    return tfidf, pkl_tfidf

@timer_with_func_name
def create_similarity_object(pkl_tfidf, dct, num_best):
    index_sim = gsm.similarities.Similarity(None, pkl_tfidf, num_features=len(dct), num_best=num_best)
    return index_sim

@timer_with_func_name
def find_key_words(num_kwords, vector, dct):
    '''
    Find num_kwords key words from vector.
    Vector must be an gensim.models.TfidfModel()[gensim.corpora.Dictionary().doc2bow(list_of_tokens)]
    '''
    top_tokens = sorted(
        vector, key=lambda x: x[1], reverse=True
    )[:num_kwords]
    head = '{: >4s}     {: >20s}     {: >5s}     {: >8s}'.format('ID', 'KEY', 'WID', 'SCORE')
    print(head)
    print('-'*len(head))
    for idn, pair in enumerate(top_tokens, start=1):
        token, score = pair
        for key, val in dct.token2id.items():
            if val == token:
                print(
                    '{: >4d}     {: >20s}     {: >5d}     {: >8.6f}'.format(idn, key,val,score)
                )
                break

##################################
#From console for refactoring ####
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