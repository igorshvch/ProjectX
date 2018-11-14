import pymorphy2
import re
from time import time

__version__ = '0.2.1'

###Content=====================================================================
###pymoprhy2 analyzer instance=================================================
MORPH = pymorphy2.MorphAnalyzer()
parser_options = {
    'parser1': (
        lambda x: MORPH.parse(x)[0][2]
    ),
    'parser2': (
        lambda x:
        MORPH.parse(x)[0].inflect({'sing', 'nomn'}).word
    )
}
PAR_TYPE = 'parser1'
PARSER = parser_options[PAR_TYPE]
#==============================================================================

def tokenize(text, word_len=0, mode='spl_single'):
    patterns = {
        'spl_single': r'\W',
        'spl_hyphen': r'[^a-zA-Zа-яА-Я0-9_-]',
        'spl_ru_hyphen': r'[^а-яА-Я0-9-]',
        'spl_ru_alph': r'[^а-яА-Я]',
        'spl_ru_alph_zero': r'[^а-яА-Я0]',
        'spl_ru_alph_hyphen': r'[^а-яА-Я-]',
        'spl_ru_alph_hyphen_zero' : r'[^а-яА-Я-0]',
        'fal_ru_hyphen' : r'\b[А-я0-9][А-я0-9-]*'
    }
    funcs = {
        'spl': re.split,
        'fal': re.findall,
    } 
    text = text.lower().strip()
    if word_len:
        return [
            token for token
            in funcs[mode[:3]](patterns.get(mode, r'\W'), text)
            if len(token)>word_len
        ]
    else:
        return [
            token for token
            in funcs[mode[:3]](patterns.get(mode, r'\W'), text)
            if token
        ]

def lemmatize(tokens_list):
    local_parser = PARSER
    return [local_parser(token) for token in tokens_list]

def lemmatize_by_map(tokens_list, mapping):
    return [mapping[token] for token in tokens_list if token in mapping]

def normalize(text, word_len=0):
    local_parser = PARSER
    text = text.lower().strip()
    if word_len:
        return [
            local_parser(token) for token
            in re.split(r'\W', text) if len(token)>word_len
        ]
    else:
        return [local_parser(token) for token in re.split(r'\W', text) if token]

def change_parser():
    global PAR_TYPE
    global PARSER
    if PAR_TYPE == 'parser1':
        PAR_TYPE = 'parser2'
        PARSER = parser_options[PAR_TYPE]
    elif PAR_TYPE == 'parser2':
        PAR_TYPE = 'parser1'
        PARSER = parser_options[PAR_TYPE]
    print('Parser was changed to {}'.format(PAR_TYPE))

class TokLem():
    def __init__(self,mapping,stpw):
        self.tok = tokenize
        self.lem = lemmatize_by_map
        self.mapping = mapping
        self.stpw = stpw
    def __call__(self, doc):
        tok_doc = self.tok(doc, mode='fal_ru_hyphen')
        cleaned_doc = [w for w in tok_doc if w not in self.stpw]
        return self.lem(cleaned_doc, self.mapping)


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
        elif sys.argv[1] == '-par_type':
            print('Parser type: {}'.format(PAR_TYPE))
        else:
            print('Not implemented!')
    except IndexError:
        print('Mode var wasn\'t passed!')