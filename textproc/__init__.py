import math
import array
from collections import Counter

from .rwtools import (
    collect_exist_files,
    collect_exist_dirs,
    collect_exist_files_and_dirs,
    read_text,
    write_text,
    save_obj,
    load_pickle
)
from .textsep import (
    separate_text
)
from .normalizer import (
    PARSER,
    tokenize,
    lemmatize,
    normalize,
    lemmatize_by_map
)
from .texttools import (
    clean_txt_and_remove_stpw,
    create_bigrams,
    form_string_numeration,
    form_string_pattern,
    time
)

def timer(func):
    def wrapper(*args, **kwargs):
        local_timer = time()
        print('-'*69)
        print('===========>DO: {:.>53}'.format(func.__name__))
        res = func(*args, **kwargs)
        print('======>COMLETE: {:.>53}'.format(func.__name__))
        end_time = time() - local_timer
        print(
            '=========>TIME: {:.3f} min ({:.3f} sec)'.format(
                end_time/60, end_time
            )
        )
        print('-'*69)
        return res
    return wrapper

def collect_docs(list_of_filepaths):
    print('Starting files processing')
    sep_docs = []
    for path in list_of_filepaths:
        sep_docs+=separate_text(read_text(path))
    print('There are {} acts in the Corpus'.format(len(sep_docs)))
    return sep_docs

@timer
def token_docs(list_of_docs, par_len=None):
    if par_len:
        list_of_docs = [
            '\n'.join(par for par in doc.split('\n') if len(par)>par_len)
            for doc in list_of_docs
        ]
    tokened_docs = [tokenize(doc) for doc in list_of_docs]
    return tokened_docs

@timer
def extract_tokens_in_doc_list(list_of_tokened_docs, path_to_stpw=None):
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
def create_posting_list(list_of_words, docs_set):
    docind = []
    for word in list_of_words:
        posting_list = [
            str(ind) for ind, set_of_tokens
            in enumerate(docs_set, start=1)
            if word in set_of_tokens
        ]
        docind.append((word, ','.join(posting_list), len(posting_list)))
    return docind

@timer
def count_term_frequences(list_of_tokened_docs):
    holder = []
    for ind, doc in enumerate(list_of_tokened_docs, start=1):
        counter = Counter(doc)
        for line in counter.items():
            holder.append((ind, *line))
    return holder

@timer
def estimate_tfidf(acts_num, words, dct_docind, dct_termfreq):
    N = acts_num+1
    dct = {i:array.array('d') for i in range(1, N)}
    holder = []
    for ind in range(1, N):
        for word in words:
            df = len(dct_docind[word])
            tfidf = (
                dct_termfreq[ind][word]
                * (math.log(N/(1 + df))+ 1)
            )
            dct[ind].append(tfidf)
        if ind % 50 == 0:
            print(ind)
    for ind in range(1, N):
        vect = dct[ind]
        lnorm = math.sqrt(sum([(inner**2) for inner in vect]))
        dct[ind] = [
            coord/lnorm
            for coord in vect
        ]
    holder = [(ind, dct[ind]) for ind in range(1, N)]
    return holder

def create_data_for_db(path_to_folder_with_txt_files,
                       par_len=None,
                       path_to_stpw=None):
    dct = {}

    list_of_filepaths = collect_exist_files(
        path_to_folder_with_txt_files,
        suffix='.txt'
    )

    timer_for_all_files = time()

    list_of_docs = collect_docs(list_of_filepaths)
    list_of_tokened_docs = token_docs(list_of_docs, par_len=par_len)
    list_of_raw_words = extract_tokens_in_doc_list(
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
