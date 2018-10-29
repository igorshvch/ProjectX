import math
import array
from collections import Counter
from time import time

from debugger import timer_with_func_name as timer
from .textproc  import (
    collect_exist_files,
    read_text,
    load_pickle
)
from .textproc.textsep import (
    separate_text
)
from .textproc.normalizer import (
    PARSER,
    tokenize,
    lemmatize_by_map
)

def collect_docs(list_of_filepaths):
    print('Starting files processing')
    sep_docs = []
    for path in list_of_filepaths:
        sep_docs+=separate_text(read_text(path))
    print('There are {} acts in the Corpus'.format(len(sep_docs)))
    return sep_docs

@timer
def token_docs(list_of_docs, mode, par_len=None):
    if par_len:
        list_of_docs = [
            '\n'.join(par for par in doc.split('\n') if len(par)>par_len)
            for doc in list_of_docs
        ]
    tokened_docs = [tokenize(doc, mode=mode) for doc in list_of_docs]
    return tokened_docs

@timer
def extract_tokens_from_doc_list(list_of_tokened_docs, path_to_stpw=None):
    set_of_raw_words = set(
        word for doc in list_of_tokened_docs for word in doc
    )
    if path_to_stpw:
        stpw = load_pickle(path_to_stpw)
        set_of_raw_words-=stpw
    list_of_raw_words = sorted(set_of_raw_words)
    print(
        'There are {:d} unique RAW'.format(len(list_of_raw_words)),
        'words in the corpus'
    )
    return list_of_raw_words

@timer
def create_lem_mapping_and_evalute_lems(list_of_raw_words):
    local_parser = PARSER
    raw_norm_word_map = {
        rw:local_parser(rw) for rw in list_of_raw_words
    }
    list_of_norm_words = sorted(set(raw_norm_word_map.values()))
    print(
        'There are {:d} unique NORM'.format(len(list_of_norm_words)),
        'words in the corpus'
    )
    return raw_norm_word_map, list_of_norm_words

@timer
def lem_docs(list_of_tokened_docs, mapping):
    lemmed_docs = [
        lemmatize_by_map(doc, mapping)
        for doc in list_of_tokened_docs
    ]
    return lemmed_docs

@timer
def create_posting_list(list_of_tokens, list_of_docs_set):
    docind = []
    dct = {token:[] for token in list_of_tokens}
    for ind, doc in enumerate(list_of_docs_set, start=1):
        for token in doc:
            dct[token].append(str(ind))
    for token in list_of_tokens:
        postlist = dct[token]
        docind.append((token, ','.join(postlist), len(postlist)))
    return docind

@timer
def count_term_frequences(list_of_tokened_docs):
    holder = []
    for ind, doc in enumerate(list_of_tokened_docs, start=1):
        counter = Counter(doc)
        for line in counter.items():
            holder.append((ind, *line))
    return holder

def create_data_for_db(path_to_folder_with_txt_files,
                       norm_mode='ru_alph_zero',
                       par_len=None,
                       path_to_stpw=None):
    dct = {}

    list_of_filepaths = collect_exist_files(
        path_to_folder_with_txt_files,
        suffix='.txt'
    )

    timer_for_all_files = time()

    list_of_docs = collect_docs(list_of_filepaths)
    list_of_tokened_docs = token_docs(
        list_of_docs, mode=norm_mode, par_len=par_len
    )
    list_of_raw_words = extract_tokens_from_doc_list(
        list_of_tokened_docs,
        path_to_stpw=path_to_stpw
    )
    raw_norm_word_map, list_of_norm_words = (
        create_lem_mapping_and_evalute_lems(list_of_raw_words)
    )
    list_of_lemmed_docs = lem_docs(
        list_of_tokened_docs, raw_norm_word_map
    )

    print('Create word sets from acts')
    local_timer = time()
    raw_acts_set = [set(doc) for doc in list_of_tokened_docs]
    norm_acts_set = [set(doc) for doc in list_of_lemmed_docs]
    print(
        'Word sets formed in',
        '{:.3f} mins'.format((time()-local_timer)/60)
    )

    docindraw = create_posting_list(list_of_raw_words, raw_acts_set)
    docindnorm = create_posting_list(list_of_norm_words, norm_acts_set)

    termfreqraw = count_term_frequences(list_of_tokened_docs)
    termfreqnorm = count_term_frequences(list_of_lemmed_docs)
    
    dct['acts'] = [[doc] for doc in list_of_docs]
    dct['wordraw'] = [[word] for word in list_of_raw_words]
    dct['wordnorm'] = [[word] for word in list_of_norm_words]
    dct['wordmapping'] = [i for i in raw_norm_word_map.items()]
    dct['docindraw'] = docindraw
    dct['docindnorm'] = docindnorm
    dct['termfreqraw'] = termfreqraw
    dct['termfreqnorm'] = termfreqnorm

    end_time = time()-timer_for_all_files
    print(
        'File(s) processed',
        'in {:.3f} mins ({:.3f} sec)'.format(end_time/60, end_time)
    )
    
    return dct
