import re
from datetime import date

from tempscripts import textproctool as tpt, iotext as it
from textproc import rwtools, PARSER, conclprep as cnp
from guidialogs import ffp, fdp

def create_doc_gen(texts_folder, patterns_file, clss, year, month, day):
    '''
    Return generator with iterates over ezch doc in a text file
    '''
    TIC = it.TextInfoCollector(texts_folder, patterns_file)
    TIC.process_files()
    return TIC.find_relevant_docs_by_date(clss, year, month, day)

def create_pkl(file_path, doc_gen):
    '''
    Return IOPickler object and write doc texts to it
    '''
    pkl = tpt.IOPickler(open(file_path, mode='w+b'))
    pkl.write(doc_gen)
    return pkl

def create_and_save_lem_map(folder_path, pkl, clss):
    '''
    Use filled with texts IOPickler object to create {'word': lemma} mapping.
    Save such mapping. Use 'cls' argumen to specify save file name by current
    data class.
    '''
    lem_map = tpt.create_lem_map(tpt.create_vocab(pkl), PARSER)
    rwtools.save_object(
        lem_map,
        '{}_{}_lem_map'.format(date.today(), clss),
        folder_path
    )
    return lem_map

def unite_concls_with_additional_data(path_to_stored_cnls, path_to_raw_cnls):
    stored_concls = rwtools.read_text(path_to_stored_cnls, encoding='utf_8_sig')
    raw_query_concls = '\n'.join(rwtools.load_pickle(path_to_raw_cnls))
    return cnp.find_concls(raw_query_concls, stored_concls)


def map_docs_to_concls(pkl, lem_map, query_concls, stpw, folder_path, clss):
    Indexer = tpt.Indexer()
    RC = tpt.ResultsCompiler()
    #1
    print('======MODEL # 01======')
    Indexer.init_model(pkl, stpw, lem_mapping=None, mode='fal_ru_hyphen', ngram_range=(1,1))
    tpt.find_acts(query_concls, Indexer, RC)
    Indexer.reset_state()
    #2
    print('======MODEL # 02======')
    Indexer.init_model(pkl, stpw, lem_mapping=lem_map, mode='fal_ru_hyphen', ngram_range=(1,1))
    tpt.find_acts(query_concls, Indexer, RC)
    Indexer.reset_state()
    #3
    print('======MODEL # 03======')
    Indexer.init_model(pkl, stpw, lem_mapping=None, mode='fal_ru_hyphen', ngram_range=(2,2))
    tpt.find_acts(query_concls, Indexer, RC)
    Indexer.reset_state()
    #4
    print('======MODEL # 04======')
    Indexer.init_model(pkl, stpw, lem_mapping=lem_map, mode='fal_ru_hyphen', ngram_range=(2,2))
    tpt.find_acts(query_concls, Indexer, RC)
    Indexer.reset_state()
    
    rwtools.save_object(RC, '{}_{}_RC_full'.format(date.today(), clss), folder_path)

    tpt.write_it(query_concls, RC)

def text_to_dct(text):
    dct = {
        '4':[],
        '9':[],
        '31':[],
        '34':[]
    }
    spl = text.split('\n')
    spl = [line.split('\t') for line in spl]
    for line in spl:
        if re.search(r'(?<=Д=)4', line[1]):
            dct['4'].append(line[0])
        elif re.search(r'(?<=Д=)9', line[1]):
            dct['9'].append(line[0])
        elif re.search(r'(?<=Д=)31', line[1]):
            dct['31'].append(line[0])
        elif re.search(r'(?<=Д=)34', line[1]):
            dct['34'].append(line[0])
    return dct

def save_dct(dct, folder_path):
    for key in dct:
        rwtools.save_object(dct[key], 'cnl_raw_{}'.format(key), folder_path)

def result_script(path_to_param_file):
    params = {}
    with open(path_to_param_file, mode='r') as f:
        lines = f.read().split('\n')
    for line in lines:
        key, val = line.split(',')
        if val.isdigit():
            val = int(val)
        params[key] = val
    assert len(params) == len(lines)
    doc_gen = create_doc_gen(
        params['texts_folder_path'],
        params['patterns_file_path'],
        params['clss'],
        params['year'],
        params['month'],
        params['day']
    )
    pkl = create_pkl(params['file_path_to_pkl'], doc_gen)
    lem_map = create_and_save_lem_map(
        params['res_folder_path'],
        pkl,
        params['clss']
    )
    query_concls = unite_concls_with_additional_data(
        params['path_to_stored_cnls'],
        params['path_to_raw_cnls']
    )
    stpw = open(params['path_to_stpw'])
    map_docs_to_concls(
        pkl,
        lem_map,
        query_concls,
        stpw,
        params['res_folder_path'],
        params['clss']
        )
    for key in sorted(params.keys()):
        print('{: <40s}: ---> {}'.format(key, params[key]))