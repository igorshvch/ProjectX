#built-in modules
from collections import Counter
from time import time

__version__ = '0.3.1'

###Content=====================================================================
def clean_txt_and_remove_stpw(par, sep, stpw):
    cleaned = [word for word in par.split(sep) if word not in stpw]
    return ' '.join(cleaned)
    
def create_bigrams(tokens_list, separator):
    separator = separator
    holder=[]
    holder = [
        separator.join((tokens_list[i-1], tokens_list[i]))
        for i in range(1, len(tokens_list), 1)
    ]
    return holder
    
def form_string_numeration(digits_num):
    st = ['{:0>', 'd}']
    form = str(digits_num).join(st)
    return form

def form_string_pattern(char, typ, fields):
    st = ['{:%s>' % char, '%s}' % typ]
    form = str(fields).join(st)
    return form

def create_vocab(pkl, normalizer, time):
    '''
    In [0]: voc = create_vocab(...)
    Act #  1000, time:    0.024 min (   1.419 sec)
    Act #  2000, time:    0.048 min (   2.854 sec)
    Act #  3000, time:    0.070 min (   4.211 sec)
    ...
    '''
    timer = time()
    gen = pkl.load_all_items()
    vocab = set()
    counter = 0
    for act in gen:
        counter+=1
        if counter % 1000 == 0:
            print('Act # {: >5d}, time: {: >8.3f} min ({: >8.3f} sec)'.format(counter, (time()-timer)/60, time() - timer))
        tokens = normalizer.tokenize(act, mode='fal_ru_hyphen')
        vocab.update(set(tokens))
    return vocab


###Testing=====================================================================
if __name__ == '__main__':
    import sys
    try:
        sys.argv[1]
        if sys.argv[1] == '-v':
            print('Module name: {}'.format(sys.argv[0]))
            print('Version info:', __version__)
        elif sys.argv[1] == '-t':
            print('Testing mode!')
            print('Not implemented!')
        else:
            print('Not implemented!')
    except IndexError:
        print('Mode var wasn\'t passed!')