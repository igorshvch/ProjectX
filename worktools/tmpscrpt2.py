from dochandl.ngdata import *
from dochandl.textproc import textsep

SUB_TABLE = {
    'п.': 'пункт',
    'пп.': 'подпункт',
    'п.п.': 'пункты',
    'ст.': 'статья',
    'ст.ст.': 'статьи',
    'стст.': 'статьи',
    'г.': 'год',
    ' - ': ' ',
    'руб.': 'рублей',
    'коп.': 'копеек',
    'к.': 'к' 
}

@timer
def f1(list_of_filepaths):
    sep = []
    for path in list_of_filepaths:
        sep+=separate_text(
            read_text(path),
            sep_func=textsep.sentence_separator,
            sub_table=SUB_TABLE
        )
    return sep
