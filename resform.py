from writer import writer
from db import overlap_score_measure

def write_to_file(con, concls, all_acts, mode='raw'):
    from writer import writer
    for ind, concl in enumerate(concls, start=1):
        holder = [concl]
        res = overlap_score_measure(con, concl, mode=mode, step = 500)
        res_s = sorted(res, key=lambda x: x[1], reverse=True)[:5]
        for act_info in res_s:
            pos, score = act_info
            act_req = all_acts[pos].split('\n')
            act_req = act_req[0] + ' ' + act_req[3]
            st = '{:<90s}'.format(act_req)+' | POSITION: {: >4d} | SCORE: {: >10.6f}'.format(pos, score)
            holder.append(st)
        writer(holder, '{}_concl_{:02d}'.format(mode.upper(), ind), mode='w')