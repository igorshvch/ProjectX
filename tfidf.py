import math
from collections import Counter
from time import time

from db import (
    fulfill_tfidf_table,
    load_all_doc_freq,
    load_all_acts,
    load_mapping
)
from textproc import timer, tokenize, lemmatize_by_map

def tfidf(N):
    def inner_f(df, tf):
        return tf*(math.log((N+1)/(df+1))+1)
    return inner_f

def euclid_norm(vect):
    return math.sqrt(sum(i**2 for i in vect))

def count_tfidf(con, mode='raw', par_len=None):
    acts_all = load_all_acts(con)
    df_all = load_all_doc_freq(con, mode=mode)

    words_all = sorted(df_all.keys())
    if par_len:
        acts_all = [
            '\n'.join(par for par in act.split('\n') if len(par)>par_len)
            for act in acts_all
        ]
    normed_acts = [tokenize(act) for act in acts_all]
    if mode == 'norm':
        mapping = load_mapping(con)
        assert len(words_all) == len(set(mapping.values()))
        normed_acts = [lemmatize_by_map(act, mapping) for act in normed_acts]

    mtrx = []
    tfidf_func = tfidf(len(acts_all))

    counter = 0
    timer = time()
    for act in normed_acts:
        counter+=1
        if counter % 10 == 0:
            local_time = time()-timer
            print(
                'Act #',
                counter,
                'TIME: {: >7.3f}m, {: >7.3f}s'.format(
                    local_time/60, local_time
                )
            )
        tf_act = Counter()
        tf_act.update(act)
        vect = {word:tf_act.get(word, 0) for word in words_all}
        vect = [tfidf_func(df_all[word], tf) for word,tf in vect.items()]
        norm = euclid_norm(vect)
        mtrx.append([val/norm for val in vect])
    return mtrx

def count_and_store_tfidf(con,
                          mode='raw',
                          step=100,
                          par_len=None):
    acts_all = load_all_acts(con)
    df_all = load_all_doc_freq(con, mode=mode)
    print(1)
    words_all = sorted(df_all.keys())
    if par_len:
        acts_all = [
            '\n'.join(par for par in act.split('\n') if len(par)>par_len)
            for act in acts_all
        ]
    normed_acts = [tokenize(act) for act in acts_all]
    if mode == 'norm':
        mapping = load_mapping(con)
        assert len(words_all) == len(set(mapping.values()))
        normed_acts = [lemmatize_by_map(act, mapping) for act in normed_acts]
    print(2)
    mtrx = []
    tfidf_func = tfidf(len(acts_all))
    print(3)
    counter = 0
    timer = time()
    for act in normed_acts:
        counter+=1
        if counter % step == 0:
            local_time = time()-timer
            print(
                'Act # {: >5d}'.format(counter),
                'TIME: {: >7.3f}m, {: >7.3f}s'.format(
                    local_time/60, local_time
                )
            )
            fulfill_tfidf_table(con, mtrx, mode=mode)
            mtrx = []
        tf_act = Counter()
        tf_act.update(act)
        vect = {word:tf_act.get(word, 0) for word in words_all}
        vect = [tfidf_func(df_all[word], tf) for word,tf in vect.items()]
        norm = euclid_norm(vect)
        str_vect = ','.join(str(val/norm) for val in vect)
        mtrx.append([str_vect])
    fulfill_tfidf_table(con, mtrx, mode=mode)
    local_time = time()-timer
    print(
        'Tfidf counting complete in',
        '{:.3f}m, {:.3f}s'.format(local_time/60, local_time)
    )
    



    

    
