#Building simple IR-system with bollean search and forword index of each
#document

import tempfile

from tempscripts import iotext as iot, textproctool as tpt
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
        self.forward_index_store = tpt.IOPickler(tempfile.TemporaryFile())
        self.inverted_index = None

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
        for ind, tokened_doc in enumerate(tknz):
            if ind % 10000 == 0:
                print(ind)
            self.create_forward_index(tokened_doc)
            tokens_set = set(tokened_doc)
            for token in tokens_set:
                iid.setdefault(token, []).append(ind)
        self.inverted_index = iid
    
    def create_forward_index(self, tokened_doc):
        holder = {}
        for ind, token in enumerate(tokened_doc):
            holder.setdefault(token, set()).add(ind)
        self.forward_index_store.append(holder)
    
    def conj_search(self, *words):
        for ind1, word in enumerate(words):
            try:
                primary_set = set(self.inverted_index[word])
            except KeyError:
                print('Word \'{}\' is not in the coprus!'.format(word))
                continue
            break       
        for ind2, word in enumerate(words[ind1:], start=ind1):
            try:
                new_set = self.inverted_index[word]
            except KeyError:
                print('There is no \'{} {}\' in the corpus!'.format(ind2, word))
                continue
            primary_set &= new_set
            if primary_set:
                final_set = primary_set
            else:
                break
        return final_set

        
        


    
