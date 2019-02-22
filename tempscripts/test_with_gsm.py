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

@timer_with_func_name
def create_dct(file, stpw, no_below, no_above, doc_delimiter=r'-{66}'):
    corpus_iterator = iot.MyReaderPre(file)
    corpus_iterator.find_docs(doc_delimiter)
    tknz = iot.Tokenizer(corpus_iterator)
    dct = gsm.corpora.Dictionary(tknz)
    stpw_ids = dct.doc2idx(stpw)
    dct.filter_tokens(bad_ids=stpw_ids)
    dct.filter_extremes(no_below=no_below, no_above=no_above, keep_n=None)
    dct.compactify()
    return dct, corpus_iterator

def save_model_on_disk(file_pkl, corpus_iterator, dct):
    pkl = tpt.IOPickler(file_pkl)
    pkl.write(dct.doc2bow(doc) for doc in iot.Tokenizer(corpus_iterator))
    return pkl