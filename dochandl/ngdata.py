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
def tokened_docs(list_of_docs, mode, par_len=None):
    if par_len:
        list_of_docs = [
            '\n'.join(par for par in doc.split('\n') if len(par)>par_len)
            for doc in list_of_docs
        ]
    list_of_tokened_docs = [
        tokenize(doc, mode=mode) for doc in list_of_docs
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
        ngram_func(doc, separator='_') for doc in list_of_tokened_docs
    ]
    return list_of_bigrammed_docs

@timer
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
                       norm_mode='ru_alph_zero',
                       ngram_func=create_bigrams,
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

    #find docs, separete and tokenise them
    list_of_docs = collect_and_sep_docs(list_of_filepaths)
    list_of_tokened_docs = tokened_docs(
        list_of_docs, mode=norm_mode, par_len=par_len
    )

    #remove stopwords if any passed to the main func
    if path_to_stpw:
        list_of_tokened_docs = clean_tokened_docs_from_stpw(
            list_of_tokened_docs, stpw
        )
    #create vocabs of unary tokens and lems, create mapping from tokens to lems
    list_of_words = extract_tokens_from_doc_list(list_of_tokened_docs)
    mapping, list_of_lemms = create_lem_mapping_and_evalute_lems(
        list_of_words
    )
    list_of_lemmed_docs = lem_docs(list_of_tokened_docs, mapping)

    #create ngrams
    list_of_tokened_docs = create_ngrams_from_tokened_docs(
        list_of_tokened_docs,
        ngram_func=create_bigrams
        )
    list_of_words = extract_tokens_from_doc_list(list_of_tokened_docs)
    list_of_lemmed_docs  = create_ngrams_from_tokened_docs(
        list_of_lemmed_docs,
        ngram_func=create_bigrams
        )
    list_of_lemms = extract_tokens_from_doc_list(list_of_lemmed_docs)

    #compute posting lists and ngrams frequencies
    tokened_docs_set = create_list_of_docs_set(list_of_tokened_docs)
    lemmed_docs_set = create_list_of_docs_set(list_of_lemmed_docs)
    tokened_pl = create_posting_list(list_of_words, tokened_docs_set)
    lemmed_pl = create_posting_list(list_of_lemms, lemmed_docs_set)
    tokened_tf = count_term_frequences(list_of_tokened_docs) 
    lemmed_tf = count_term_frequences(list_of_lemmed_docs)

    #store valuable information in a dict
    dct['acts'] = [[doc] for doc in list_of_docs]
    dct['wordraw'] = [[word] for word in list_of_words]
    dct['wordnorm'] = [[word] for word in list_of_lemms]
    dct['wordmapping'] = [i for i in mapping.items()]
    dct['docindraw'] = tokened_pl
    dct['docindnorm'] = lemmed_pl
    dct['termfreqraw'] = tokened_tf
    dct['termfreqnorm'] = lemmed_tf

    end_time = time()-timer_for_all_files
    print(
        'File(s) processed',
        'in {:.3f} mins ({:.3f} sec)'.format(end_time/60, end_time)
    )
    
    return dct

def prepare_concl(concl_txt,
                  path_to_stpw=None,
                  norm_mode='ru_alph_zero',
                  ngram_func=create_bigrams):
    if path_to_stpw:
        stpw = load_pickle(path_to_stpw)
    timer_for_all_files = time()

    tokens = tokenize(concl_txt, mode=norm_mode)
    if path_to_stpw:
        tokens = [token for token in tokens if token not in stpw]
    lemms = lemmatize(tokens)
    tokened_bigrams = create_bigrams(tokens, separator='_')
    lemmed_bigrams = create_bigrams(lemms, separator='_')

    end_time = time()-timer_for_all_files
    print(
        'Concl processed',
        'in {:.3f} mins ({:.3f} sec)'.format(end_time/60, end_time)
    )
    
    return ' '.join(tokened_bigrams), ' '.join(lemmed_bigrams)
