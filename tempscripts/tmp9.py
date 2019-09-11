import re
from time import strftime
from collections import Counter

import pymorphy2

from textproc import rwtools
from tempscripts import iopickler as iop

morph = pymorphy2.MorphAnalyzer()
parse = morph.parse

dt_stamp = '%Y-%m-%d#%a#%H-%M-%S'

def process_corpus(doc_store, iop_obj, sep=10000):
    cd = CashDicts()
    ws = Counter()
    counter_d = 0
    counter_w1 = 0
    counter_w2 = 0
    for doc in doc_store:
        counter_d += 1
        if counter_d % sep == 0:
            print('Docs:', counter_d)
            print('Totlal words:',counter_w1)
        doc = doc['Текст документа']
        tl, ws = tokenize(doc, ws)
        counter_w1 = len(ws)
        iop_obj.append(tl)
    for word in ws:
        counter_w2 += 1
        if counter_w2 % sep == 0:
            print('Processed words:',counter_w2)
        nf, tag = parser(word)
        cd.fill_dicts(word, nf, tag)
        cd.doc_freq = ws
    return cd

def tokenize(doc, tokens_set):
    doc = doc.lower()
    tokens_list = re.findall(r'\b[а-я][а-я-]*', doc)
    tokens_set.update(set(tokens_list))
    #tokens_set |= set(tokens_list)
    return tokens_list, tokens_set

def parser(word):
    word_meta = parse(word)[0]
    normal_form = word_meta.normal_form
    POS_tag = str(word_meta.tag.POS)
    return normal_form, POS_tag

def clean_corpus_with_dict(loader, saver, dct, sep=10000):
    '''
    General function for lemmatization
    and cleaning text with a dictionary object
    '''
    counter = 0
    for doc in loader:
        counter += 1
        if counter % sep == 0:
            print('Docs: ', counter)
        doc = [dct[word] for word in doc if word in dct]
        saver.append(doc)
    
def clean_corpus_with_set(loader, saver, set_c, sep=10000):
    '''
    General function for lemmatization
    and cleaning text with a dictionary object
    '''
    counter = 0
    for doc in loader:
        counter += 1
        if counter % sep == 0:
            print('Docs: ', counter)
        doc = [word for word in doc if word in set_c]
        saver.append(doc)

def create_bigrams(loader, saver, sep=10000):
    counter = 0
    for doc in loader:
        counter += 0
        if counter % 10000:
            print('Docs: ', counter)
        doc = [
            doc[i-1]+'#'+doc[i]
            for i in range(1, len(doc), 1)
        ]
        saver.append(doc)


class CashDicts():
    def __init__(self):
        self.__dict_names = (
            'token_nf',
            'token_tag',
            'tag_token',
            'tag_nf',
            'nf_token',
            'nf_tag',
            'doc_freq'
        )
        self.token_nf = dict()
        self.token_tag = dict()
        self.tag_token = dict()
        self.tag_nf = dict()
        self.nf_token = dict()
        self.nf_tag = dict()
        self.doc_freq = dict()
    
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


class OnDiscDictWrapper():
    def __init__(self, folder):
        self.__dict_names = (
            'token_nf',
            'token_tag',
            'tag_token',
            'tag_nf',
            'nf_token',
            'nf_tag',
            'doc_freq'
        )
        self.folder = folder
        self.save_files = dict()
        self.files_created_flag = False
        self.create_files()
    
    def __getattr__(self, name):
        if name in (
            'token_nf',
            'token_tag',
            'tag_token',
            'tag_nf',
            'nf_token',
            'nf_tag',
            'doc_freq'
        ):
            return self.__open_dict(name)
        elif name in self.__dict__:
            return self.__dict__[name]
        else:
            raise AttributeError(name)
    
    def __setattr__(self, name, val):
        if name in (
            'token_nf',
            'token_tag',
            'tag_token',
            'tag_nf',
            'nf_token',
            'nf_tag',
            'doc_freq'
        ):
            self.__write_dict(name, val)
        else:
            self.__dict__[name] = val
    
    def create_files(self):
        if not self.files_created_flag:
            fp = rwtools.collect_exist_files(self.folder, suffix='.dct')
            if fp:
                for file in fp:
                    name = file.name.split('#')[0]
                    self.save_files[name] = str(file)
            else:
                for dictionary in self.__dict_names:
                    name = dictionary + '#' +strftime(dt_stamp) + '.dct'
                    file = rwtools.create_new_binary(name, self.folder)
                    self.save_files[dictionary] = file.name
                    file.close()
            self.files_created_flag = True
    
    def __open_dict(self, dictionary):
        return rwtools.load_pickle(self.save_files[dictionary], mode='rb')
    
    def __write_dict(self, dictionary, val):
        rwtools.save_pickle(
            val,
            self.save_files[dictionary]
        )
    
    def erase_dict(self, dictionary):
        breaker = input(
            'You are going to delete dictionary "{}" '.format(dictionary)
            + 'entierly! Please confirm!("Y"/"N")\n'
        )
        if breaker == 'N':
            print ('Operation aborted')
            return None
        elif breaker == 'Y':
            with open(self.save_files[dictionary], mode='wb') as f:
                f.truncate(0)
        else:
            print('Incorrect command! Operation aborted')
    
    def erase_all_dicts(self):
        breaker = input(
            'You are going to delete all dictionaries'
            + 'entierly! Please confirm!("Y"/"N")\n'
        )
        if breaker == 'N':
            print ('Operation aborted')
            return None
        elif breaker == 'Y':
            for dictionary in self.save_files:
                with open(self.save_files[dictionary], mode='wb') as f:
                    f.truncate(0)
        else:
            print('Incorrect command! Operation aborted')
    
    def store_external_dicts(self, dicts_iter):
        for dictionary, dct in dicts_iter:
            print(dictionary)
            rwtools.save_pickle(
                dct,
                self.save_files[dictionary]
            )