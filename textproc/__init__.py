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

def create_data_for_db(path_to_folder_with_txt_files):
    dct = {}
    docindraw = []
    docindnorm = []

    local_parser = PARSER

    all_text_files = collect_exist_files(
        path_to_folder_with_txt_files,
        suffix='.txt'
    )

    time_for_all_files = time()
    print('Starting files processing')
    sep_acts = []
    for path in all_text_files:
        sep_acts+=separate_text(read_text(path))
    print('There are {} acts in the Corpus'.format(len(sep_acts)))
        
    print('Count words')
    raw_words = set(word for act in sep_acts for word in tokenize(act))
    print('There are {:d} words in corpus'.format(len(raw_words)))

    print('Normalize words')
    local_timer = time()
    raw_norm_word_map = {rw:local_parser(rw) for rw in raw_words}
    raw_words = sorted(raw_words)
    norm_words = sorted(set(raw_norm_word_map.values()))
    print(
        'Normalization complete in',
        '{:.3f} mins'.format((time()-local_timer)/60)
    )

    print('Split acts into tokens and lemms')
    local_timer = time()
    raw_acts = [tokenize(act) for act in sep_acts]
    norm_acts = [
        lemmatize_by_map(act, raw_norm_word_map)
        for act in raw_acts
    ]
    #Probably following two assignment statemnts should assign to
    #'raw_acts' and 'norm_acts' respectivly insted of using two new
    #names
    raw_acts_set = [set(act) for act in raw_acts]
    norm_acts_set = [set(act) for act in norm_acts]
    print(
        'Spliting complete in',
        '{:.3f} mins'.format((time()-local_timer)/60)
    )

    print('Form posting lists for raw words')
    time_for_raw_postings = time()
    for raw_word in raw_words:
        posting_list = [
            str(ind) for ind, list_of_tokens
            in enumerate(raw_acts_set, start=1)
            if raw_word in list_of_tokens
        ]
        docindraw.append((raw_word, ','.join(posting_list)))
    print(
        'Posting lists were formed for RAW words',
        'in {:.3f} mins'.format((time()-time_for_raw_postings)/60)
    )

    print('From posting lists for norm words')
    time_for_norm_postings = time()
    for norm_word in norm_words:
        posting_list = [
            str(ind) for ind, list_of_tokens
            in enumerate(norm_acts_set, start=1)
            if norm_word in list_of_tokens
        ]
        docindnorm.append((norm_word, ','.join(posting_list)))
    print(
        'Posting lists were formed for NORM words',
        'in {:.3f} mins'.format((time()-time_for_norm_postings)/60)
    )
    dct['acts'] = [[act] for act in sep_acts]
    dct['wordraw'] = [[word] for word in raw_words]
    dct['wordnorm'] = [[word] for word in norm_words]
    dct['wordmapping'] = [i for i in raw_norm_word_map.items()]
    dct['docindraw'] = docindraw
    dct['docindnorm'] = docindnorm

    print(
        'Files processed',
        'in {:.3f} mins'.format((time()-time_for_all_files)/60)
    )
    
    return dct
