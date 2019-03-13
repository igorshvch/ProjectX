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
    head = '{: >20s}     {: >5s}     {: >8s}'.format('KEY', 'ID', 'SCORE')
    print(head)
    print('-'*len(head))
    for token, score in top_tokens:
        for key, val in dct.token2id.items():
            if val == token:
                print(
                    '{: >20s}     {: >5d}     {: >8.6f}'.format(key,val,score)
                )
                break