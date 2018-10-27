import math
import array
import itertools
from collections import Counter
from time import time

from debugger import timer_with_func_name as timer
from .textproc.rwtools import (
    collect_exist_files,
    collect_exist_dirs,
    collect_exist_files_and_dirs,
    read_text,
    save_obj,
    load_pickle
)
from .textproc.textsep import (
    separate_text
)
from .textproc.normalizer import (
    PARSER,
    tokenize,
    lemmatize,
    normalize,
    lemmatize_by_map
)
from .textproc.texttools import (
    clean_txt_and_remove_stpw,
    create_bigrams
)

@timer
def collect_and_sep_docs(list_of_filepaths):
    print('Starting files processing')
    sep_docs = []
    for path in list_of_filepaths:
        sep_docs+=separate_text(read_text(path))
    print('There are {} acts in the Corpus'.format(len(sep_docs)))
    return sep_docs

@timer
def tokened_docs(list_of_docs, par_len=None):
    if par_len:
        list_of_docs = [
            '\n'.join(par for par in doc.split('\n') if len(par)>par_len)
            for doc in list_of_docs
        ]
    list_of_tokened_docs = [
        tokenize(doc, mode='hyphen') for doc in list_of_docs
    ]
    return list_of_tokened_docs

@timer
def clean_tokened_docs_from_stpw(list_of_tokened_docs, stpw):
    cleaned_tokened_docs = [
        [word for word in doc if word not in stpw] 
        for doc in list_of_tokened_docs
    ]
    return cleaned_tokened_docs

@timer
def extract_tokens_from_doc_list(list_of_tokened_docs):
    set_of_raw_ngrams = set(
        itertools.chain.from_iterable(list_of_tokened_docs)
    )
    list_of_raw_ngrams = sorted(set_of_raw_ngrams)
    print(
        'There are {:d} unique RAW'.format(len(list_of_raw_ngrams)),
        'words in the corpus'
    )
    return list_of_raw_ngrams

@timer
def create_lem_mapping_and_evalute_lems(list_of_raw_ngrams):
    local_parser = PARSER
    raw_norm_word_map = {
        rw:local_parser(rw) for rw in list_of_raw_ngrams
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
def create_ngrams_from_tokened_docs(list_of_tokened_docs,
                                    ngram_func=create_bigrams):
    list_of_bigrammed_docs = [
        ngram_func(doc) for doc in list_of_tokened_docs
    ]
    return list_of_bigrammed_docs

@time
def create_list_of_docs_set(list_of_tokened_docs):
    list_of_docs_set = [set(doc) for doc in list_of_tokened_docs]
    return list_of_docs_set

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
                       par_len=None,
                       path_to_stpw=None):
    if path_to_stpw:
        stpw = load_pickle(path_to_stpw)
    
    dct = {}
    
    list_of_filepaths = collect_exist_files(
        path_to_folder_with_txt_files,
        suffix='.txt'
    )

    timer_for_all_files = time()

    ##############

    list_of_docs = collect_and_sep_docs(list_of_filepaths)
    list_of_tokened_docs = tokened_docs(list_of_docs, par_len=par_len)
    if path_to_stpw:
        list_of_tokened_docs = clean_tokened_docs_from_stpw(
            list_of_tokened_docs, stpw
        )
    list_of_words = extract_tokens_from_doc_list(list_of_tokened_docs)
    mapping, list_of_lemms = create_lem_mapping_and_evalute_lems(
        list_of_words
    )
    list_of_lemmed_docs = lem_docs(list_of_tokened_docs, mapping)



    ##############

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