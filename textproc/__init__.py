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
        print('-'*69)
        local_timer = time()
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
    sep_acts = []
    for path in list_of_filepaths:
        sep_acts+=separate_text(read_text(path))
    print('There are {} acts in the Corpus'.format(len(sep_acts)))
    return sep_acts

@timer
def token_docs(list_of_docs):
    tokened_docs = [tokenize(doc) for doc in list_of_docs]
    return tokened_docs

@timer
def extract_tokens_in_doc_list(list_of_tokened_docs):
    set_of_raw_words = set(
        word for doc in list_of_tokened_docs for word in doc
    )
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
        docind.append((word, ','.join(posting_list)))
    return docind

@timer
def count_term_frequences(list_of_tokened_docs):
    holder = []
    for ind, doc in enumerate(list_of_tokened_docs, start=1):
        counter = Counter(doc)
        for line in counter.items():
            holder.append((ind, *line))
    return holder    

def create_data_for_db(path_to_folder_with_txt_files):
    dct = {}

    list_of_filepaths = collect_exist_files(
        path_to_folder_with_txt_files,
        suffix='.txt'
    )

    timer_for_all_files = time()

    list_of_docs = collect_docs(list_of_filepaths)
    list_of_tokened_docs = token_docs(list_of_docs)
    list_of_raw_words = extract_tokens_in_doc_list(list_of_tokened_docs)
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

    print(
        'File(s) processed',
        'in {:.3f} mins'.format((time()-timer_for_all_files)/60)
    )
    
    return dct
