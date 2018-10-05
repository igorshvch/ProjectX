#built-in modules
from collections import Counter
from time import time

__version__ = '0.2.1'

###Content=====================================================================
def clean_txt_and_remove_stpw(par, sep, stpw):
    cleaned = [word for word in par.split(sep) if word not in stpw]
    return ' '.join(cleaned)
    
def create_bigrams(tokens_list):
    separator = BGRINR_B
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