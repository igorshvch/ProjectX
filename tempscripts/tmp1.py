from textproc import rwtools

def transmute(item, st):
    lst = [i.strip() for i in item.split('|')]
    res_dct = {}
    for item in lst[1:]:
        try:
            key, val = item.split(':')
            res_dct[key.strip()] = [val.strip()]
        except:
            print(item, st, 'something')
    res_dct['ALG'] = []
    if 'POSITION' not in res_dct:
        res_dct['POSITION'] = []
    if 'SCORE' not in res_dct:
        res_dct['SCORE'] = []
    return lst[0], res_dct

def txt_concls_to_dct(folder_path):
    res_dct = {}
    concls_dct = {}
    paths = rwtools.collect_exist_files(folder_path, suffix='.txt')
    #print('Len paths', len(paths))
    for path in paths:
        alg_name = path.stem[:-8]
        text = rwtools.read_text(path)
        concl, _, *acts = text.strip().split('\n')  
        concl_num = path.stem[-2:]
        #print(path.stem, concl_num)
        concls_dct[concl_num] = concl
        if len(acts)>0:
            acts = [act for act in acts if act]
        else:
            continue
        if concl_num not in res_dct:
            res_dct[concl_num] = {}
        for act in acts:
            name, specs = transmute(act, path.stem)
            if name not in res_dct[concl_num]:
                res_dct[concl_num][name] = specs
                res_dct[concl_num][name]['ALG'].append(alg_name)
            else:
                res_dct[concl_num][name]['POSITION'].append(specs['POSITION'][0])
                res_dct[concl_num][name]['SCORE'].append(specs['SCORE'][0])
                res_dct[concl_num][name]['ALG'].append(alg_name)
    return res_dct, concls_dct

def transform_dct_to_txt(dct, cnl_dct, b=0.15, acts=5):
    from writer import writer
    options = {
        '2018-11-09__efficient_cosine_similarity_RAW_BIGRAMS_': 'RB',
        '2018-11-09__efficient_cosine_similarity_RAW__': 'R',
        '2018-11-09__efficient_cosine_similarity_NORM_BIGRAMS_': 'NB',
        '2018-11-09__efficient_cosine_similarity_NORM__': 'N'
    }
    for key in sorted(dct.keys()):
        holder = [cnl_dct[key]]
        holder.append('='*144)
        #cnl_dct[key],'='*96
        inner_holder = []
        for act in dct[key]:
            assert len(set(dct[key][act]['POSITION'])) == 1
            pos = int(dct[key][act]['POSITION'][0])
            score = sum(float(i) for i in dct[key][act]['SCORE'])
            alg = (
                ','.join(options[algr] for algr in dct[key][act]['ALG'])
            )
            inner_holder.append((act, pos, score, alg))
        inner_holder = sorted(inner_holder, key=lambda x: x[2], reverse=True)
        for info in inner_holder:
            if info[2] > b:
                st = (
                    '{:<90s}'.format(info[0])
                    +' | POSITION: {: >4d} | SCORE: {: >10.6f}'.format(info[1], info[2])
                    +' | ALG: {: >9s}'.format(info[3])
                )
                holder.append(st)
        writer(holder[:(acts+2)], 'holder_concl_{}'.format(key), mode='w', verbose=False)

def count_acts(folder_path):
    paths = rwtools.collect_exist_files(folder_path, suffix='.txt')
    counter = 0
    for p in paths:
        text=rwtools.read_text(p)
        spl = text.split('\n')
        counter += len(spl[2:])
    return counter

def find_similars(st):
    spl = st.split('\n')
    spl = set([row[:91].rstrip(' ') for row in spl if row])
    print(len(spl))
    for i in spl: print(i)
    return spl



            
                
                
            
        

        
