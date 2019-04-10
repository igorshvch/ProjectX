import re
from . import rwtools

###Content=====================================================================
ARTICLE = r'Статья [0-9]{1,4}.*'
THEME = r'[0-9]{1,3}.*'
QUESTION = r'\t[0-9]{1,3}.*'
POSITION = r'\t\tПозиция.*'

STRIP = '1234567890 !"#$%&\'()*+,./:;<=>?@[\\]^_`{|}~'


ARTICLE_CLEANED = (
    r'(?<=Статья ').*
)

DESICION_CLEANED = (
    r'(?<=Вывод из судебной практики: ).*'
)

DESICION_CLEANED_POS = (
    r'(?<=По вопросу о).*(?=у судов нет единой позиции|существует две позиции судов|существует три позиции судов|существует четыре позиции судов|существует пять позиций судов)'
)

POSITION_CLEANED = r'(?<=Позиция [1-9]\.).*'

PATTERNS = {
    'art': ARTICLE,
    'thm' : THEME,
    'qst' : QUESTION,
    'pos': POSITION,
    'dc': DESICION_CLEANED,
    'p': POSITION_CLEANED
}

def process_exist_concls(text, debug=False):
    spl = text[:-1].split('\n')
    questions = []
    current_question = None
    positions = []
    errors = []
    for ind, line in enumerate(spl):
        if re.match(ARTICLE, line):
            current_article = re.match(ARTICLE, line).group()
        elif re.match(THEME, line):
            current_theme = current_article, re.match(THEME, line).group()
        elif re.match(QUESTION, line):
            questions.append(
                (ind, *current_theme, re.match(QUESTION, line).group())
            )
            current_question = None
        elif re.match(POSITION, line):
            if current_question:
                positions.append(
                    (ind, *current_question, re.match(POSITION, line).group())
                )
            else:
                current_question = questions.pop()[1:]
                positions.append(
                    (ind, *current_question, re.match(POSITION, line).group())
                )
        else:
            errors.append('{:0>4d} >>> {}'.format(ind, line))
        res = sorted(questions + positions, key = lambda x: x[0])
        res = [[*item[1:]] for item in res]
    if debug:
        return res, questions, positions, errors
    else:
        return res

def clean_article(text):
    pass


def func(cleaned_dec, stored_dec):
    from writer import writer
    holder_errors = []
    holder_res = []
    cleaned_dec = [line.replace('Вывод из судебной практики: ', '') for line in cleaned_dec]
    cleaned_dec = [line.replace('\n', '') for line in cleaned_dec]
    spl_cl = [line.split('#')+['',''] for line in cleaned_dec]
    print('spl_cl', len(spl_cl))
    spl_st = [line.split('#')+['',''] for line in stored_dec]
    print('spl_st', len(spl_st))
    dct_com =  {(item[0]+item[1].strip('.')).replace(' ', ''):item[0]+'#'+item[1].strip('.') for item in spl_cl}
    print('dct_com', len(dct_com))
    spl_cl_keys = [(item[0]+item[1].strip('.')).replace(' ', '') for item in spl_cl]
    spl_st_keys = [(item[0]+item[1]).replace(' ', '') for item in spl_st]
    spl_cl = [item[2:] for item in spl_cl]
    spl_st = [item[2:] for item in spl_st]
    writer(spl_st_keys, 'spl_st_keys', mode='w')
    writer(list(dct_com.keys()), 'dct_com_keys', mode='w')
    flag_fisrt = True
    for ind, key in enumerate(dct_com.keys()):
        print(ind, end=' :: ')
        try:
            pos_in_st = spl_st_keys.index(key)
            print ('pos_in_st', pos_in_st,)
        except:
            print('error!', end=' == ')
            holder_errors.append(key)
            continue
        pos_in_cl = spl_cl_keys.index(key)
        if flag_fisrt:
            pos_in_st+=1
        while pos_in_st:
            if flag_fisrt:
                flag_fisrt = False
                pos_in_st-=1
            st = '#'.join([dct_com[key], *spl_st[pos_in_st], *spl_cl[pos_in_cl]])
            holder_res.append(st)
            pos_in_st+=1
            pos_in_cl+=1
            try:
                val = spl_st_keys[pos_in_st]
            except:
                pos_in_st = None
            if val != key:
                break
    holder_res = [re.subn('#{1,4}', '#', line)[0].rstrip('#') for line in holder_res]
    return holder_res, holder_errors

def cleaner(string):
    holder = []
    spl = [line.lstrip('0123456789. ') for line in string.split('#')]
    for line in spl:
        if re.search(PATTERNS['dc'], line):
            holder.append(re.search(PATTERNS['dc'], line).group())
        elif re.search(PATTERNS['p'], line):
            holder.append(re.search(PATTERNS['p'], line).group())
        else:
            holder.append(line)
    return ' '.join(holder)
        

def clean_string_from_pattern(lst):
    holder = []
    for item in lst:
        res = cleaner(item)
        holder.append(res)
    return holder