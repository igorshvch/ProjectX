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

def generate_data_for_db(path_to_folder_with_txt_files):
    dct = {}
    docindraw = {}
    docindnorm = []
    counter = 1

    local_parser = PARSER

    all_text_files = collect_exist_files(
        path_to_folder_with_txt_files,
        suffix='.txt'
    )

    for path in all_text_files:
        print('Starting file # {:0>3d}!'.format(counter))
        time_for_one_file = time()

        sep_acts = separate_text(read_text(path))

        print('Count words')
        raw_words = [word for act in sep_acts for word in tokenize(act)]
        print('There are {:0>7d} words in corpus'.format(len(raw_words)))

        print('Normalize words')
        raw_norm_word_map = {rw:local_parser(rw) for rw in raw_words}
        raw_words = sorted(raw_norm_word_map.keys())
        norm_words = sorted(raw_norm_word_map.values())

        ('Split acts into tokens and lemms')
        raw_acts = [tokenize(act) for act in sep_acts]
        norm_acts = [
            lemmatize_by_map(act, raw_norm_word_map)
            for act in sep_acts
        ]

        print('From posting lists for raw words')
        time_for_raw_postings = time()
        for raw_word in raw_words:
            posting_list = [
                ind for ind, list_of_tokens
                in enumerate(raw_acts)
                if raw_word in list_of_tokens
            ]
            docindraw[raw_word] = posting_list
        print(
            'Posting lists were formed for RAW words',
            'in {:03.3f} mins'.format((time()-time_for_raw_postings)/60)
        )

        print('From posting lists for norm words')
        time_for_norm_postings = time()
        for norm_word in norm_words:
            posting_list = [
                ind for ind, list_of_tokens
                in enumerate(norm_acts)
                if norm_word in list_of_tokens
            ]
            docindnorm[raw_word] = posting_list
        print(
            'Posting lists were formed for NORM words',
            'in {:0>3.3f} mins'.format((time()-time_for_norm_postings)/60)
        )
        dct['acts'] = sep_acts
        dct['raw_words'] = raw_words
        dct['norm_words'] = norm_words
        dct['mapping'] = raw_norm_word_map
        dct['docindraw'] = docindraw
        dct['docindnorm'] = docindnorm

        print(
            'File # {:0>3d} processed'.format(counter),
            'in {:0>3.3f}'.format((time()-time_for_one_file)/60)
        )
        counter+=1
        
        yield dct