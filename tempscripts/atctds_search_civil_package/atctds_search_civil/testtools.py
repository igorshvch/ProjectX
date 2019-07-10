import random as rd
import re

from .textproc import rwtools
from .debugger import timer

def generate_tokens_secquence(length=5):
    alph = [chr(i) for i in range(97, 123, 1)]
    holder = []
    while length:
        holder.append(''.join(rd.choices(alph, k=rd.randint(3,7))).capitalize())
        length-=1
    return holder

gts = generate_tokens_secquence

def test_find_positions_by_pattern(folder, pattern):
    '''
    Testing.
    Find positons of text sequences corresponding
    to the pattern passed as argument
    '''
    holder = []
    last_pos = -1
    fp = rwtools.collect_exist_files(folder, suffix='.txt')
    for path in fp:
        print(path.name)
        holder.append(str(fp))
        with open(path, mode='r') as file:
            while True:
                line = file.readline()
                cur_pos = file.tell()
                if re.match(pattern, line):
                    holder.append(cur_pos)
                if last_pos ==  cur_pos:
                    break
                else:
                    last_pos = cur_pos
    return holder

def test_simple_text_gen(words_num, alph=1040):
    '''
    Testing.
    Generate semi-text sequences for further indexing tests
    '''
    alph = [chr(i) for i in range(alph, alph+32)]
    res = []
    while words_num:
        length = rd.randint(1, 20)
        res.append(''.join(rd.sample(alph, k=length)))
        words_num -= 1
    return res

@timer
def test_indexer(docs, vocab=None, tokenizer=None):
    '''
    Testing.
    Create primitive inverted index table on passed iterable with tokened docs
    '''
    if vocab:
        inner_voc = vocab
    else:
        inner_voc = dict()
    for ind, doc in enumerate(docs):
        if tokenizer:
            doc = tokenizer(doc)
        for token in set(doc):
            inner_voc.setdefault(token, []).append(ind)
    return inner_voc

def test_word_expand(word, morph=None):
    '''
    Query word expander. Use pymorphy2 'MorphAnalyzer' instance

    -> In[0]: test_word_expand('взносы')
    -> Out[79]: 
    -> ['взнос',
        'взноса',
        ...
        'взносах'] 
    '''
    w = morph.parse(word)[0]
    res = [i[0] for i in w.lexeme]
    return res