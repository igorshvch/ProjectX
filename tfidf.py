import math
from collections import Counter
from time import time

from db import (
    fulfill_tfidf_table,
    load_num_of_docs,
    load_all_doc_freq,
    load_all_acts,
    load_all_words,
    load_mapping,
    iterate_row_loading,
    find_all_words,
    load_tfidf_vector
)
from dochandl import tokenize, lemmatize, lemmatize_by_map

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

def overlap_score_measure(con, query_text, mode='raw', step=100):
    if mode == 'raw':
        table='tfidfraw'
    elif mode == 'norm':
        table='tfidfnorm'
    query_text = tokenize(query_text)
    if mode == 'norm':
        query_text = lemmatize(query_text)
    vocab = {
        word:position for position,word
        in enumerate(load_all_words(con, words=mode))
    }
    positions = [vocab[word] for word in query_text if word in vocab]
    gen = iterate_row_loading(con, table, ('vector',), step=step)
    holder = []
    inner_ind = 0
    local_timer = time()
    for ind, batch in enumerate(gen, start=1):
        local_time = time() - local_timer
        print(
            'Batch # {: >3d}'.format(ind),
            'TIME: {: >6.3f}m, {: >8.3f}s'.format(local_time/60, local_time)
        )
        for inner_ind, row in enumerate(batch, start=inner_ind):
            vector = row[0].split(',')
            vector = [float(coord) for coord in vector]
            holder.append((inner_ind, sum(vector[pos] for pos in positions)))
        inner_ind += 1
    return holder

def estimate_query_vect(con, query_text, mode='raw'):
    query_text = tokenize(query_text)
    if mode == 'norm':
        query_text = lemmatize(query_text)
    cnt = Counter()
    cnt.update(query_text)
    tfidf_func = tfidf(load_num_of_docs(con))
    df = load_all_doc_freq(con, mode=mode)
    all_words = load_all_words(con, words=mode)
    vect = [(cnt.get(word,0), word) for word in all_words]
    vect = [tfidf_func(df[word], tf) if tf else 0 for tf, word in vect]
    norm = euclid_norm(vect)
    vect = [c/norm for c in vect]
    return vect

def cosine_similarity(con, query_vect, mode='raw', step=100):
    if mode == 'raw':
        table='tfidfraw'
    elif mode == 'norm':
        table='tfidfnorm'
    gen = iterate_row_loading(con, table, ('vector',), step=step)
    holder = []
    inner_ind = 0
    local_timer = time()
    for ind, batch in enumerate(gen, start=1):
        local_time = time() - local_timer
        print(
            'Batch # {: >3d}'.format(ind),
            'TIME: {: >6.3f}m, {: >8.3f}s'.format(local_time/60, local_time)
        )
        for inner_ind, row in enumerate(batch, start=inner_ind):
            vector = row[0].split(',')
            vector = [float(coord) for coord in vector]
            result = sum(c1*c2 for c1, c2 in zip(query_vect, vector))
            holder.append((inner_ind, result))
        inner_ind += 1
    return holder

def aggr_query_vect_cos_sim(con, query_text, mode, step=500):
    query_vect = estimate_query_vect(con, query_text, mode=mode)
    return cosine_similarity(con, query_vect, mode=mode, step=step)

def efficient_cosine_similarity(con, query_text, mode='raw'):
    res_holder = []
    #df_all = load_all_doc_freq(con, mode=mode)
    all_words = load_all_words(con, words=mode)
    query_vect = estimate_query_vect(con, query_text, mode=mode)
    vect_data = [
        (word, score) for word, score
        in zip(all_words, query_vect) if score>0
    ]
    vect_data = sorted(vect_data, key = lambda x: x[1], reverse=True)[:10]
    base_similarity_condition = [word for word, score in vect_data if len(word)>2]
    while base_similarity_condition:
        print('{: <6s} : {:d}'.format('BSC', len(base_similarity_condition)))
        acts_ind = find_all_words(
            con, base_similarity_condition, mode=mode, inden='\t'
        )
        acts_found = len(acts_ind)
        print('{: <6s} : {:d}'.format('acts_l', acts_found))
        if acts_found >= 5:
            break
        base_similarity_condition.pop()
        if len(base_similarity_condition) == 2:
            break
    print(acts_ind)
    for ind in acts_ind:
        #print(ind)
        vector = load_tfidf_vector(con, ind, mode=mode).split(',')
        vector = [float(coord) for coord in vector]
        result = sum(c1*c2 for c1, c2 in zip(query_vect, vector))
        res_holder.append((int(ind)-1, result))
    res_holder = sorted(res_holder, key=lambda x:x[1], reverse=True)
    if len(res_holder) > 8:
        return res_holder[:8]
    else:
        return res_holder


    



    

    
