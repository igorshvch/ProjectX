#Building simple IR-system with bollean search and forword index of each
#document

import iotext as iot
from debugger import timer_with_func_name

@timer_with_func_name
def create_inverted_index(corpus_iterator, stpw, tknz, **tknz_kwargs):
    '''
    Unefficient function for creating inverted index table
    corpus_iterator - iterable with strings each of wich represrents document
    tknz - iot.Tokenizer class instance or iot.Tokenizer descendante 
           class instance
    stpw - iterable with stopwords
    tknz_kwargs - keyword arguments for tknz object which are
                  delim, word_len, lem_map
    '''
    iid = {}
    tknz = tknz(corpus_iterator, stpw)
    for ind, tokens_doc in enumerate(tknz):
        if ind % 10000 == 0:
            print(ind)
        tokens_set = set(tokens_doc)
        for token in tokens_set:
            iid.setdefault(token, []).append(ind)
    return iid

class BooleanSearcher():
    '''
    Class implementes boolean serach by constracting inverted indices table
    and also forward indices tables for each document
    '''
    def __init__(self):
        self.iid = None

    @timer_with_func_name
    def create_inverted_index(self, corpus_iterator, stpw, tknz, **tknz_kwargs):
        '''
        Unefficient function for creating inverted index table
        corpus_iterator - iterable with strings each of wich represrents document
        tknz - iot.Tokenizer class instance or iot.Tokenizer descendante 
            class instance
        stpw - iterable with stopwords
        tknz_kwargs - keyword arguments for tknz object which are
                    delim, word_len, lem_map
        '''
        iid = {}
        tknz = tknz(corpus_iterator, stpw)
        for ind, tokens_doc in enumerate(tknz):
            if ind % 10000 == 0:
                print(ind)
            tokens_set = set(tokens_doc)
            for token in tokens_set:
                iid.setdefault(token, []).append(ind)
        self.iid = iid
    
