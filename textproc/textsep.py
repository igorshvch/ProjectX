from re import (
    subn, DOTALL, split, match
)
from time import time

###Content=====================================================================
#Patterns
PATTERN_ACT_CLEAN1 = '-{66}\nКонсультантПлюс.+?-{66}\n'
PATTERN_ACT_CLEAN2 = 'КонсультантПлюс.+?\n.+?\n'
PATTERN_ACT_CLEAN3 = r'Рубрикатор ФАС \(АСЗО\).*?Текст документа\n'
PATTERN_ACT_SEP1 = '\n\n\n-{66}\n\n\n'
PATTERN_ACT_SEP2 = 'Документ предоставлен КонсультантПлюс'
PATTERN_PASS1 = (
    'ОБЗОР\nСУДЕБНОЙ ПРАКТИКИ ПО ДЕЛАМ,'
    '+ РАССМОТРЕННЫМ\nАРБИТРАЖНЫМ СУДОМ УРАЛЬСКОГО ОКРУГА'
)
PATTERN_PASS2 = (
    'Утвержден\nпрезидиумом Арбитражного суда\nСеверо-Кавказского округа'
)
PUNCTUATION = '!"#$%&\'()*+,/:;<=>?@[\\]^`{|}~_'


#Funcs
def court_decisions_cleaner(text, inden=''):
    t0 = time()
    cleaned_text1 = subn(PATTERN_ACT_CLEAN1, '', text, flags=DOTALL)[0]
    cleaned_text2 = subn(PATTERN_ACT_CLEAN2, '', cleaned_text1)[0]
    cleaned_text3 = subn(
        PATTERN_ACT_CLEAN3, '', cleaned_text2, flags=DOTALL
        )[0]
    print('{}Acts were cleaned in {:->3.5f} seconds'.format(inden, time()-t0))
    return cleaned_text3[1:-68]

def court_decisions_separator(text, sep_type='sep1', inden='', mode='ret'):
    t0 = time()
    if sep_type=='sep1':
        separated_acts = split(PATTERN_ACT_SEP1, text)
    else:
        separated_acts = split(PATTERN_ACT_SEP2, text)
    separated_acts = [
        act for act in separated_acts
        if not match(PATTERN_PASS1, act)
        and not match(PATTERN_PASS2, act)
    ]
    print(
        '{}Acts were separated in {:->3.5f} seconds,'.format(inden, time()-t0),
        '{} acts were found'.format(len(separated_acts))
    )
    if mode=='ret':
        return separated_acts
    elif mode=='gen':
        yield separated_acts
    else:
        raise ValueError('Incorrect mode kwarg: {}'.format(mode))

def sentence_separator(text, sep_type='sep1', inden='', sub_table=None):
    separated_acts = court_decisions_separator(
        text, sep_type=sep_type, inden=inden
    )
    text = '\n'.join(separated_acts)
    for key in sub_table:
        text = text.replace(key, sub_table[key])
    text = subn(r'\b[А-Я]\.[А-Я]*\.*', '', text)[0]
    text = subn(r'[%s]'%PUNCTUATION, '', text)[0]
    text = subn(r'\b[0-9]{1,2}\.[0-9]{2}\.[0-9]{2,4}', '', text)[0]
    text = subn(r' {2,}', ' ', text)[0]
    pre_sents = text.lower().split('.')
    sentences = []
    for pre_s in pre_sents:
        spl_s = pre_s.split('\n')
        for sent in spl_s:
            if len(sent) > 74:
                sentences.append(sent.strip())
    return sentences

def separate_text(text,
                  inden='',
                  clean_func=court_decisions_cleaner,
                  sep_func=court_decisions_separator,
                  **kwargs):
    return sep_func(clean_func(text, inden=inden), inden=inden, **kwargs)
    

###Testing=====================================================================
if __name__ == '__main__':
    print('Not implemented!')