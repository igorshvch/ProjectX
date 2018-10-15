import math
from collections import Counter
from time import time

from db import fulfill_tfidf_table
from query import (
    load_all_doc_freq,
    load_all_acts
)
from textproc import timer
from textproc.normalizer import tokenize

def tfidf(N):
    def inner_f(df, tf):
        return tf*(math.log((N+1)/(df+1))+1)
    return inner_f

def euqlid_norm(vect):
    return math.sqrt(sum(i**2 for i in vect))

def count_tfidf(con, mode='raw'):
    #work only for raw words!!!
    acts_all = load_all_acts(con)
    df_all = load_all_doc_freq(con, mode=mode)

    words_all = sorted(df_all.keys())
    tokened_acts = [tokenize(act) for act in acts_all]

    mtrx = []
    tfidf_func = tfidf(len(acts_all))

    counter = 0
    timer = time()
    for act in tokened_acts:
        counter+=1
        if counter % 10 == 0:
            local_time = time()-timer
            print('Act #', counter, 'TIME: {:.3f}m, {:.3f}s'.format(local_time/60, local_time))
        tf_act = Counter()
        tf_act.update(act)
        vect = {word:tf_act.get(word, 0) for word in words_all}
        vect = [tfidf_func(df_all[word], tf) for word,tf in vect.items()]
        norm = euqlid_norm(vect)
        mtrx.append([val/norm for val in vect])
    return mtrx

def count_and_store_tfidf(con, mode='raw', step=100):
    #work only for raw words!!!
    acts_all = load_all_acts(con)
    df_all = load_all_doc_freq(con, mode=mode)
    print(1)
    words_all = sorted(df_all.keys())
    tokened_acts = [tokenize(act) for act in acts_all]
    print(2)
    mtrx = []
    tfidf_func = tfidf(len(acts_all))
    print(3)
    counter = 0
    timer = time()
    for act in tokened_acts:
        counter+=1
        if counter % step == 0:
            local_time = time()-timer
            print(
                'Act #',
                counter,
                'TIME: {:.3f}m, {:.3f}s'.format(local_time/60, local_time)
            )
            fulfill_tfidf_table(con, mtrx, mode=mode)
            mtrx = []
        tf_act = Counter()
        tf_act.update(act)
        vect = {word:tf_act.get(word, 0) for word in words_all}
        vect = [tfidf_func(df_all[word], tf) for word,tf in vect.items()]
        norm = euqlid_norm(vect)
        str_vect = ','.join(str(val/norm) for val in vect)
        mtrx.append([str_vect])
    fulfill_tfidf_table(con, mtrx)
    print(
        'Tfidf counting complete in',
        '{:.3f}m, {:.3f}s'.format(local_time/60, local_time)
    )
    



    

    
