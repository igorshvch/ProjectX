from writer import writer
from tfidf import (
    overlap_score_measure,
    estimate_query_vect
)
from db import load_all_words

def OSM_write_to_file(con, concls, all_acts, mode='raw'):
    from writer import writer
    for ind, concl in enumerate(concls, start=1):
        holder = [concl, '='*127]
        res = overlap_score_measure(con, concl, mode=mode, step = 500)
        res_s = sorted(res, key=lambda x: x[1], reverse=True)[:5]
        for act_info in res_s:
            pos, score = act_info
            act_req = all_acts[pos].split('\n')
            act_req = act_req[0] + ' ' + act_req[3]
            st = (
                '{:<90s}'.format(act_req)
                +' | POSITION: {: >4d} | SCORE: {: >10.6f}'.format(pos, score)
            )
            holder.append(st)
        writer(
            holder,
            '{}_{}_concl_{:02d}'.format(
                OSM_write_to_file.__name__[:3],
                mode.upper(),
                ind
            ),
            mode='w'
        )

def default_write_to_file(con,
                          concls,
                          all_acts,
                          func,
                          mode=None,
                          step=500,
                          filenameadder=''):
    options ={
        (1,1):lambda con,concl,mode,step: func(con,concl,mode=mode,step=step),
        (1,0):lambda con,concl,mode,step: func(con,concl,mode=mode),
        (0,1):lambda con,concl,mode,step: func(con,concl,step=step),
        (0,0):lambda con,concl,mode,step: func(con,concl)
    }
    from writer import writer
    for ind, concl in enumerate(concls, start=1):
        holder = [concl, '='*127]
        #if mode:
        #    res = func(con, concl, mode=mode, step = step)
        #else:
        #    res = func(con, concl, step = step)
        res = options[bool(mode), bool(step)](con, concl, mode, step)
        res_s = sorted(res, key=lambda x: x[1], reverse=True)[:5]
        for act_info in res_s:
            pos, score = act_info
            act_req = all_acts[pos].split('\n')
            act_req = act_req[0] + ' ' + act_req[3]
            st = (
                '{:<90s}'.format(act_req)
                +' | POSITION: {: >4d} | SCORE: {: >10.6f}'.format(pos, score)
            )
            holder.append(st)
        writer(
            holder,
            '{}_{}_concl_{:02d}{}'.format(
                func.__name__,
                mode.upper(),
                ind,
                filenameadder
            ),
            mode='w'
        )

def write_to_file(res, all_acts, file_name):
    from writer import writer
    holder = []
    for act_info in res:
        pos, score = act_info
        act_req = all_acts[pos].split('\n')
        act_req = act_req[0] + ' ' + act_req[3]
        st = (
            '{:<90s}'.format(act_req)
            +' | POSITION: {: >4d} | SCORE: {: >10.6f}'.format(pos, score)
        )
        holder.append(st)
    writer(holder, file_name, mode='w')

def concl_words_tfidf_score(con, concl, mode='raw', filenameadder=None):
    all_words = load_all_words(con, words=mode)
    vector = estimate_query_vect(con, concl, mode=mode)
    vect_data = [
        (word, score) for word, score
        in zip(all_words, vector) if score>0
    ]
    vect_data = sorted(vect_data, key = lambda x: x[1], reverse=True)
    holder = (
        [concl]
        +['='*96]
        +[
            '{:.<30s} {: >10.7f}'.format(word, score)
            for word, score in vect_data
        ]
        +['='*96]
    )
    writer(
        holder,
        'vect_{}_data_{}'.format(mode.upper(),
        filenameadder), mode='w'
    )