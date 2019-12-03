import re
import array
from time import time, strftime
from collections import Counter

import pymorphy2

from textproc import rwtools
from tempscripts import iopickler as iop

morph = pymorphy2.MorphAnalyzer()
parse = morph.parse

dt_stamp = '%Y-%m-%d#%a#%H-%M-%S'

def main(corpus_iterator, project_name, main_folder):
    try:
        print('Documents in total:', len(corpus_iterator))
    except:
        print('Corpus length unavailable')
    import pathlib as pthl
    ######1
    time_subtotal = None
    time_start_0 = time()
    time_start = time()
    ######2

    file_tk = rwtools.create_new_binary(project_name+'.tk', main_folder)
    file_tk_set = rwtools.create_new_binary(
        project_name+'.tk_set', main_folder
    )
    file_lm = rwtools.create_new_binary(project_name+'.lm', main_folder)
    file_lm_set = rwtools.create_new_binary(
        project_name+'.lm_set', main_folder
    )
    file_bg_tk = rwtools.create_new_binary(project_name+'.bgtk', main_folder)
    file_bg_lm = rwtools.create_new_binary(project_name+'.bglm', main_folder)
    file_inv_index = rwtools.create_new_binary(
        project_name+'.ii', main_folder
    )

    iop_obj_tk = iop.IOPickler(file_tk)
    iop_obj_tk_set = iop.IOPickler(file_tk_set)
    iop_obj_lm = iop.IOPickler(file_lm)
    iop_obj_lm_set = iop.IOPickler(file_lm_set)
    iop_obj_bg_tk = iop.IOPickler(file_bg_tk)
    iop_obj_bg_lm = iop.IOPickler(file_bg_lm)
    iop_obj_inv_index = iop.IOPickler(file_inv_index)

    file_tk = file_tk_set = file_lm = file_lm_set = None 
    file_bg_tk = file_bg_lm = file_inv_index= None

    pthl.Path(main_folder).joinpath('DictHolder').mkdir(
        parents=True, exist_ok=True
    )

    dct_wrap = OnDiscDictWrapper(
        str(pthl.Path(main_folder).joinpath('DictHolder'))
    )

    cash_dct = process_corpus(corpus_iterator, iop_obj_tk, iop_obj_tk_set)
    ######1
    time_subtotal = time()
    mins = (time_subtotal - time_start) // 60
    sec = (time_subtotal - time_start) % 60
    print(
        'Dictionaries were created: {: >3.0f} min, {: >6.3f} sec'.format(mins, sec)
    )
    time_start = time_subtotal
    ######2
    dct_wrap.store_external_dicts(cash_dct.upload_dicts())
    ######1
    time_subtotal = time()
    mins = (time_subtotal - time_start) // 60
    sec = (time_subtotal - time_start) % 60
    print(
        'Dictionaries were saved: {: >3.0f} min, {: >6.3f} sec'.format(mins, sec)
    )
    time_start = time_subtotal
    ######2
    corpus_stats = {
        'corp_len': len(iop_obj_tk),
        'total dif tokens': len(cash_dct.token_nf),
        'total dif lemms': len(cash_dct.nf_tag),
    }
    del cash_dct

    lemmatize(iop_obj_tk, iop_obj_lm, iop_obj_lm_set, dct_wrap.token_nf)
    ######1
    time_subtotal = time()
    mins = (time_subtotal - time_start) // 60
    sec = (time_subtotal - time_start) % 60
    print(
        'Corpus was lemmatized: {: >3.0f} min, {: >6.3f} sec'.format(mins, sec)
    )
    time_start = time_subtotal
    ######2
    create_bigrams(iop_obj_tk, iop_obj_bg_tk)
    ######1
    time_subtotal = time()
    mins = (time_subtotal - time_start) // 60
    sec = (time_subtotal - time_start) % 60
    print(
        'Bg_tk was created: {: >3.0f} min, {: >6.3f} sec'.format(mins, sec)
    )
    time_start = time_subtotal
    ######2
    create_bigrams(iop_obj_lm, iop_obj_bg_lm)
    ######1
    time_subtotal = time()
    mins = (time_subtotal - time_start) // 60
    sec = (time_subtotal - time_start) % 60
    print(
        'Bg_lm was created: {: >3.0f} min, {: >6.3f} sec'.format(mins, sec)
    )
    time_start = time_subtotal
    ######2
    dct_indicies = create_inv_index(iop_obj_tk_set, iop_obj_inv_index)
    dct_wrap.inv_index = dct_indicies
    ii_wraper = InvertedIndexWrapper(
        dct=dct_indicies,
        ii_table=iop_obj_inv_index
    )
    ######1
    time_subtotal = time()
    mins = (time_subtotal - time_start) // 60
    sec = (time_subtotal - time_start) % 60
    print(
        'Inverted index created: {: >3.0f} min, {: >6.3f} sec'.format(
            mins, sec
        )
    )
    ######2
    ######1
    time_subtotal = time()
    mins = (time_subtotal - time_start_0) // 60
    sec = (time_subtotal - time_start_0) % 60
    print(
        'Total time cost: {: >3.0f} min, {: >6.3f} sec'.format(mins, sec)
    )
    ######2

    return {
        'invind': ii_wraper,
        'dcts': dct_wrap,
        'tk': iop_obj_tk,
        'tk_set': iop_obj_tk_set,
        'lm': iop_obj_lm,
        'lm_set': iop_obj_lm_set,
        'bgtk': iop_obj_bg_tk,
        'bglm': iop_obj_bg_lm,
        'ii': iop_obj_inv_index,
        'stats': corpus_stats
    }




##########################################

def process_corpus(doc_store, saver_doc_tok, saver_doc_set, sep=10000):
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
        #doc = doc['Текст документа']
        tl, ws = tokenize(doc, ws, saver_doc_set)
        counter_w1 = len(ws)
        saver_doc_tok.append(tl)
    for word in ws:
        counter_w2 += 1
        if counter_w2 % sep == 0:
            print('Processed words:',counter_w2)
        nf, tag = parser(word)
        cd.fill_dicts(word, nf, tag)
    cd.doc_freq = ws
    return cd

def tokenize(doc, tokens_set, saver_set):
    doc = doc.lower()
    tokens_list = re.findall(r'\b[а-я][а-я-]*', doc)
    tokens_ad_hoc_set = set(tokens_list)
    tokens_set.update(tokens_ad_hoc_set)
    saver_set.append(tokens_ad_hoc_set)
    #tokens_set |= set(tokens_list)
    return tokens_list, tokens_set

def parser(word):
    word_meta = parse(word)[0]
    normal_form = word_meta.normal_form
    POS_tag = str(word_meta.tag.POS)
    return normal_form, POS_tag

#################################

def lemmatize(loader, saver_list, saver_set, dct, sep=10000):
    '''
    Custom function for tokens lemmatization and set_of_lemms making
    '''
    for ind, doc in enumerate(loader):
        if ind % sep == 0:
            print('Docs: ', ind)
        doc = [dct[word] for word in doc if word in dct]
        doc_set = set(doc)
        saver_list.append(doc)
        saver_set.append(doc_set)

def clean_corpus_with_dict(loader, saver, dct, sep=10000):
    '''
    General function for lemmatization
    and cleaning text with a dictionary object
    '''
    for ind, doc in enumerate(loader):
        if ind % sep == 0:
            print('Docs: ', ind)
        doc = [dct[word] for word in doc if word in dct]
        saver.append(doc)
    
def clean_corpus_with_set(loader, saver, set_c, sep=10000):
    '''
    General function for lemmatization
    and cleaning text with a dictionary object
    '''
    for ind, doc in enumerate(loader):
        if ind % sep == 0:
            print('Docs: ', ind)
        doc = [word for word in doc if word in set_c]
        saver.append(doc)

def create_bigrams(loader, saver, sep=10000):
    for ind, doc in enumerate(loader):
        if ind % sep == 0:
            print('Docs: ', ind)
        doc = [
            doc[i-1]+'#'+doc[i]
            for i in range(1, len(doc), 1)
        ]
        saver.append(doc)

def create_inv_index(loader, saver, sep=10000):
    dct_words = {}
    dct_indicies = {}
    for ind, doc in enumerate(loader):
        if ind % sep == 0:
            print('Docs: ', ind)
        for word in doc:
            dct_words.setdefault(word, array.array('l')).append(ind)
    print('Start writing')
    counter = 0
    while dct_words:
        key, item = dct_words.popitem()
        saver.append(item)
        dct_indicies[key] = counter
        counter += 1
        if counter % sep == 0:
            print('Docs: ', counter)
    return dct_indicies

def load_previous_session(folder):
    ####1
    time0 = time()
    ####2
    options = {
        'bglm': lambda x: iop.IOPickler(x),
        'bgtk': lambda x: iop.IOPickler(x),
        'ii': lambda x: iop.IOPickler(x),
        'lm': lambda x: iop.IOPickler(x),
        'lm_set': lambda x: iop.IOPickler(x),
        'tk': lambda x: iop.IOPickler(x),
        'tk_set': lambda x: iop.IOPickler(x)
    }
    res_dct = {}
    dct_wrap = OnDiscDictWrapper(folder)
    ####1
    sub_time = time() - time0
    print(
        'Dicts loaded: {: >3.0f} min, {: >6.3f} sec'.format(
            sub_time // 60, sub_time % 60
        )
    )
    time1 = time()
    ####2
    fp = rwtools.collect_exist_files(folder)
    for path in fp:
        suffix = path.suffix[1:]
        if suffix in options:
            print('Loading {}'.format(suffix))
            res_dct[suffix] = options[suffix](open(str(path), mode='rb'))
            ####1
            sub_time = time() - time1
            print(
                'Iterator {} loaded: {: >3.0f} min, {: >6.3f} sec'.format(
                    suffix, sub_time // 60, sub_time % 60
                )
            )
            time1 = time()
            ####2
    res_dct['invind'] = InvertedIndexWrapper(
        dct=dct_wrap.inv_index,
        ii_table = res_dct['ii']
    )
    ####1
    sub_time = time() - time1
    print(
        'InIndex loaded: {: >3.0f} min, {: >6.3f} sec'.format(
            sub_time // 60, sub_time % 60
        )
    )
    time1 = time()
    ####2
    corpus_stats = {
        'corp_len': len(res_dct['tk']),
        'total dif tokens': len(dct_wrap.token_nf),
        'total dif lemms': len(dct_wrap.nf_tag),
    }
    res_dct['dcts'] = dct_wrap
    res_dct['stats'] = corpus_stats
    ####1
    total_time = time() - time0
    print(
        'Loading time: {: >3.0f} min, {: >6.3f} sec'.format(
            total_time // 60, total_time % 60
        )
    )
    ####2
    return res_dct



###########################################
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
            'doc_freq',
            'inv_index'
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
            'doc_freq',
            'inv_index'
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
            'doc_freq',
            'inv_index'
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
            #print(dictionary)
            rwtools.save_pickle(
                dct,
                self.save_files[dictionary]
            )
    

class InvertedIndexWrapper():
    def __init__(self, dct=None, ii_table=None, main_folder=None):
        self.__keys = dct
        self.__inverted_index = ii_table
        if main_folder:
            self.__folder = main_folder
            self.__keys, self.__inverted_index = self.__load_data(main_folder)
        else:
            self.__folder = None
    
    def __iter__(self):
        for key in self.__keys:
            yield key

    def __getitem__(self, item):
        if item in self.__keys:
            word_index = self.__keys[item]
            doc_indicies = self.__inverted_index[word_index]
            return doc_indicies
    
    def __load_data(self, folder):
        files_with_keys = rwtools.collect_exist_files(folder, suffix='.dct')
        for file_path in files_with_keys:
            if 'inv_index' in str(file_path):
                file_key = str(file_path)
                break
        file_with_table = rwtools.collect_exist_files(folder, suffix='.ii')
        file_with_table = str(file_with_table.pop())
        return rwtools.load_pickle(file_key), iop.IOPickler(file_with_table)


class CorpusBuffer():
    def __init__(self,
                 word_pos_dct,
                 stop_words={},
                 word_len=0,
                 POSes=None,
                 ):
        self.word_pos_dct = word_pos_dct
        self.stop_words = stop_words
        self.word_len = word_len
        self.POSes = POSes
    
    def __call__(self, doc):
        return self.__main(doc)

    def __main(self, doc):
        holder = []
        for token in doc:
            if (
                len(token) > self.word_len
                and token not in self.stop_words
                and self.word_pos_dct[token] in self.POSes
            ):
                holder.append(token)
        return holder
