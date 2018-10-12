from collections import Counter

from query import (
    load_all_doc_freq,
    load_all_acts
)
from textproc.normalizer import tokenize

def count_tfidf(con, mode='raw'):
    #work only for raw words!!!
    acts_all = load_all_acts(con)
    df_all = load_all_doc_freq(con, mode=mode)

    words_all = sorted(df_all.keys())
    tokened_acts = [tokenize(act) for act in acts_all]

    for act in tokened_acts:
        counter = Counter()
        counter.update(act)
        for word in words_all:
            vect = {word:0 for word in words_all}



    

    
