import re

import pymorphy2

morph = pymorphy2.MorphAnalyzer()
parse = morph.parse

def process_corpus(doc_store, iop_obj):
    cd = CashDicts()
    ws = set() 
    for doc in doc_store:
        doc = doc['Текст документа']
        tl, ws = tokenize(doc, ws)
        iop_obj.append(tl)
    for word in ws:
        nf, tag = parser(word)
        cd.fill_dicts(word, nf, tag)
    return cd

def tokenize(doc, tokens_set):
    doc = doc.lower()
    tokens_list = re.findall(r'\b[а-я0-9][а-я0-9-]*', doc)
    tokens_set |= set(tokens_list)
    return tokens_list, tokens_set

def parser(word):
    word_meta = parse(word)[0]
    normal_form = word_meta.normal_form
    POS_tag = str(word_meta.tag.POS)
    return normal_form, POS_tag

class CashDicts():
    def __init__(self):
        self.__dict_names = (
            'token_nf',
            'token_tag',
            'tag_token',
            'tag_nf',
            'nf_token',
            'nf_tag'
        )
        self.token_nf = dict()
        self.token_tag = dict()
        self.tag_token = dict()
        self.tag_nf = dict()
        self.nf_token = dict()
        self.nf_tag = dict()
    
    def fill_dicts(self, token, normal_form, tag):
        self.tag_token.setdefault(tag, set()).add(token)
        self.tag_nf.setdefault(tag, set()).add(normal_form)
        self.nf_token.setdefault(normal_form, set()).add(token)
        self.nf_tag[normal_form] = tag
        self.token_nf[token] = normal_form
        self.token_tag[token] = tag
    
    def upload_dicts(self):
        for dictionary in self.__dict_names:
            yield dictionary, self.__dict__[dictionary]