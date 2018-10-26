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

def collect_docs(list_of_filepaths):
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
    tokened_docs = [tokenize(doc, mode='hyphen') for doc in list_of_docs]
    return tokened_docs

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
        ngram_func(doc) for doc in tokened_docs
    ]
    return list_of_bigrammed_docs

@time
def create_list_of_docs_set(list_of_tokened_docs):
    list_of_docs_set = [set(doc) for doc in list_of_tokened_docs]
    return list_of_docs_set

@timer
def create_posting_list(list_of_words, list_of_docs_set):
    docind = []
    for word in list_of_words:
        posting_list = [
            str(ind) for ind, set_of_tokens
            in enumerate(docs_set, start=1)
            if word in set_of_tokens
        ]
        docind.append((word, ','.join(posting_list), len(posting_list)))
    return docind
