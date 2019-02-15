import pickle
import functools
import math
from collections import Counter
from time import time

import numpy as np
import scipy.sparse
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

from atctds_search.debugger import timer
from atctds_search.textproc.normalizer import tokenize, TokLem, PARSER
from atctds_search.textproc import rwtools, textsep

class IOPickler():
    def __init__(self, file):
        self.file = file
        self.indexer = []
        self.file_name = file.name
    
    def __getitem__(self, int_num):
        try:
            pos = self.indexer[int_num]
        except IndexError:
            return 'Position is out of index'
        return self._load_item(pos)
    
    def __len__(self):
        return len(self.indexer)
    
    def _load_item(self, pos):
        if self.file.closed:
            return 'File is closed!'
        self.file.seek(pos)
        #unpick = pickle.Unpickler(self.file)
        return pickle.load(self.file)
    
    def reopen(self):
        if not self.file.closed:
            return 'File is opened!'
        self.file = open(self.file.name, mode='a+b')
    
    def close(self):
        if self.file.closed:
            return 'File is closed!'
        self.file.close()

    @timer
    def write(self, data_iterable):
        if self.file.closed:
            return 'File is closed!'
        self.file.seek(0)
        self.indexer = []
        #pick = pickle.Pickler(self.file)
        for item in data_iterable:
            self.indexer.append(self.file.tell())
            pickle.dump(item, self.file)
    
    def load_all_items(self, pos=0):
        if self.file.closed:
            return 'File is closed!'
        self.file.seek(self.indexer[pos])
        #unpick = pickle.Unpickler(self.file)
        error = False
        while not error:
            try:
                item = pickle.load(self.file)
                yield item
            except:
                error = True

    def create_index(self):
        if self.indexer:
            return 'Index already exists!'
        self.file.seek(0)
        gen = self.load_all_items(pos=0)
        while True:
            self.indexer.append(self.file.tell())
            try:
                next(gen)
            except:
                break
        self.indexer.pop()
    
    def append(self, item):
        if self.file.closed:
            return 'File is closed!'
        self.file.seek(0, 2)
        self.indexer.append(self.file.tell())
        #pick = pickle.Pickler(self.file)
        pickle.dump(item, self.file)
    
    def erase(self):
        self.file.truncate(0)
        self.indexer=[]

##################################################

def create_docgen(folder):
    filepaths = rwtools.collect_exist_files(folder, suffix='.txt')
    docgen = (doc for path in filepaths for doc in textsep.separate_text(rwtools.read_text(path)))
    return docgen

def create_vocab(pkl):
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
        tokens = tokenize(act, mode='fal_ru_hyphen')
        vocab.update(set(tokens))
    return vocab

def create_lem_map(vocab, parser=PARSER):
    local_parser = PARSER
    return {word:local_parser(word) for word in vocab}

##################################################

def flags_changer(key):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            args[0].flags[key] = True
            return func(*args, **kwargs)
        return wrapper
    return decorator

class TestFlagsChanger():
    def __init__(self):
        self.flags = {
            'tfidf':False,
            'tokenizer':False,
            'weighttable':False
        }
    @flags_changer('tfidf')
    def tfidf(self):
        print('Flag \'tfidf\' status: {}'.format(self.flags['tfidf']))
    @flags_changer('tokenizer')
    def tokenizer(self):
        print('Flag \'tokenizer\' status: {}'.format(self.flags['tokenizer']))
    @flags_changer('weighttable')
    def weighttable(self):
        print('Flag \'weighttable\' status: {}'.format(self.flags['weighttable']))
    def reset_flags(self):
        self.flags = {key:False for key in self.flags}

class Indexer():
    def __init__(self):
        self.TL = None
        self.tfv = None
        self.cnt_v = None
        self.iopickler = None
        self.mtrx = None
        self.N = None
        self.poses = {}
        self.df = None
        self.flags ={
            'tfidf' : False,
            'tokenizer' : False,
            'weighttable' : False,
            'all_df' : False,
            'poses' : False
        }
    
    def _reset_flags(self):
        self.flags = {key:False for key in self.flags}
    
    def reset_state(self):
        self.TL = None
        self.tfv = None
        self.cnt_v = None
        self.iopickler = None
        self.mtrx = None
        self.N = None
        self.poses = {}
        self.df = None
        self._reset_flags()

    @flags_changer('tokenizer')
    def init_tokenizer(self, stpw, lem_mapping, mode='fal_ru_hyphen'):
        r'''
        tokenization patterns (modes):
        'spl_single': r'\W',
        'spl_hyphen': r'[^a-zA-Zа-яА-Я0-9_-]',
        'spl_ru_hyphen': r'[^а-яА-Я0-9-]',
        'spl_ru_alph': r'[^а-яА-Я]',
        'spl_ru_alph_zero': r'[^а-яА-Я0]',
        'spl_ru_alph_hyphen': r'[^а-яА-Я-]',
        'spl_ru_alph_hyphen_zero' : r'[^а-яА-Я-0]',
        'fal_ru_hyphen' : r'\b[А-я0-9][А-я0-9-]*'
        '''
        self.TL = TokLem(stpw, lem_mapping=lem_mapping, mode=mode)
    
    @flags_changer('tfidf')
    def init_vectorizers(self, ngram_range=(1,1)):
        if not self.flags['tokenizer']:
            return 'Tokenizer is not initialized'
        self.tfv = TfidfVectorizer(
            tokenizer=self.TL,
            ngram_range=ngram_range
        )
        self.cnt_v = CountVectorizer(
            binary = True,
            tokenizer=self.TL,
            ngram_range=ngram_range
        )
    
    @flags_changer('weighttable')
    def init_tfidf_table(self, doc_iter):
        if not self.flags['tfidf']:
            return 'Tfidf Vectorizer is not initialized'
        self.mtrx = self.tfv.fit_transform(doc_iter)
        self.N = self.mtrx.shape[0]
        self.N_words = self.mtrx.shape[1]
    
    @flags_changer('all_df')
    def create_df_index(self, doc_iter):
        cnt_mtrx = self.cnt_v.fit_transform(doc_iter)
        self.cnt_v = None
        sum_vect = cnt_mtrx.sum(axis=0, dtype=int)
        self.df = np.squeeze(np.asarray(sum_vect))
    
    @flags_changer('poses')
    def create_pos_index(self):
        if not self.flags['weighttable']:
            return 'Tfidf indices are not estimated'
        self.poses = {ind:word for word,ind in self.tfv.vocabulary_.items()}
    
    def init_model(self,
                   iopickler_obj,
                   stpw,
                   lem_mapping=None,
                   mode='fal_ru_hyphen',
                   ngram_range=(1,1)):
        self.iopickler = iopickler_obj
        local_time = time()
        self.init_tokenizer(stpw, lem_mapping, mode=mode)
        print(
            '{:-<17s} : {:_>7.3f} min ({:_>8.3f} sec)'.format(
                'init_tokenizer', (time()-local_time)/60, time()-local_time
            )
        )
        self.init_vectorizers(ngram_range=ngram_range)
        print(
            '{:-<17s} : {:_>7.3f} min ({:_>8.3f} sec)'.format(
                'init_vectorizers', (time()-local_time)/60, time()-local_time
            )
        )
        self.init_tfidf_table(iopickler_obj.load_all_items())
        print(
            '{:-<17s} : {:_>7.3f} min ({:_>8.3f} sec)'.format(
                'init_tfidf_table', (time()-local_time)/60, time()-local_time
            )
        )
        self.create_df_index(iopickler_obj.load_all_items())
        print(
            '{:-<17s} : {:_>7.3f} min ({:_>8.3f} sec)'.format(
                'create_df_index', (time()-local_time)/60, time()-local_time
            )
        )
        self.create_pos_index()
        print(
            '{:-<17s} : {:_>7.3f} min ({:_>8.3f} sec)'.format(
                'create_pos_index', (time()-local_time)/60, time()-local_time
            )
        )
    
    def _define_used_alg(self):
        options = {
            (1, 1) : 'NB',
            (0, 1) : 'RB',
            (1, 0) : 'N',
            (0, 0) : 'R'
        }
        val1 = 0 if self.TL.lem_mapping == 'raw' else bool(self.TL.lem_mapping)
        val2 = 1 if self.tfv.ngram_range == (2,2) else 0
        return options[(val1, val2)]
    
    def _query_find_word_positions(self, text_string, method='tfidf'):
        if not self.flags['poses']:
            return 'Poses index is not created!'
        if not self.flags['weighttable'] and method == 'tfidf':
            return 'Tfidf indices are not estimated!'
        if not self.flags['all_df'] and (method == 'df' or method == 'idf'):
            return 'Docfreq indices are not estimated!'
        vect = self.tfv.transform([text_string])
        vect = vect.toarray().flatten()
        if method == 'tfidf':
            return zip(np.nonzero(vect)[0], vect[np.nonzero(vect)])
        if method == 'df' or method == 'idf':
            return np.nonzero(vect)[0]
    
    def query_find_most_valuable_words(self,
                                       text_string,
                                       words_quant=10,
                                       method='tfidf'):
        res = self._query_find_word_positions(text_string, method=method)
        if isinstance(res, str):
            return res
        if method == 'tfidf':
            vect = [(self.poses[ind], score) for ind,score in res]
        elif method == 'df':
            vect = [(self.poses[ind], self.df[ind]) for ind in res]
        elif method == 'idf':
            vect = [
                (self.poses[ind], math.log(self.N/self.df[ind]))
                for ind in res
            ]
        words_quant = words_quant if len(vect) > words_quant else -1
        reverse = True if method != 'df' else False
        if words_quant == -1:
            return sorted(vect, key=lambda x : x[1], reverse=reverse)
        else:
            return sorted(
                vect, key=lambda x : x[1], reverse=reverse
            )[:words_quant]
    
    def query_find_similar_acts(self, text_string, border=(3,3), words_quant=10):
        alg_mark = self._define_used_alg()
        query_vect = self.tfv.transform([text_string])
        key_words = self.query_find_most_valuable_words(
            text_string, words_quant=words_quant, method='tfidf'
        )
        key_words_indices = [
            self.tfv.vocabulary_[word] 
            for word, score in key_words
        ]
        doc_ind_holder = []
        for index in key_words_indices:
            vect = self.mtrx[:,index].toarray().flatten()
            doc_ind_holder.append(
                set(np.nonzero(vect)[0])
            )
        while True:
            res_indices = doc_ind_holder[0].intersection(*doc_ind_holder[1:])
            len_res_indices = len(res_indices)
            if len_res_indices >= border[1]:
                break
            doc_ind_holder.pop()
            if len(doc_ind_holder) == border[0]:
                break
        if not res_indices:
            return 'Search finished without results!'
        vectors = [
            (ind, self.mtrx[ind,:].toarray().flatten())
            for ind in res_indices
        ]
        scores = [(ind, sum(query_vect*vect)) for ind, vect in vectors]
        scores = sorted(scores, key=lambda x: x[1], reverse=True)
        res_holder = []
        for item in scores:
            ind, score = item
            doc = self.iopickler[ind].split('\n')
            req = doc[0] + ' ' + doc[3]
            res_holder.append((req, score, alg_mark, ind))
        return res_holder
    
    def save_model(self, folder_path):
        rwtools.save_object(self.TL, 'TL.model', folder_path)
        rwtools.save_object(self.tfv, 'tfv.model', folder_path)
        rwtools.save_object(self.cnt_v, 'cnt_v.model', folder_path)
        scipy.sparse.save_npz(folder_path+r'\mtrx.npz', self.mtrx)
        rwtools.save_object(self.N, 'N.model', folder_path)
        rwtools.save_object(self.poses, 'poses.model', folder_path)
        rwtools.save_object(self.df, 'df.model', folder_path)
        rwtools.save_object(self.flags, 'flags.model', folder_path)
    
    def load_model(self, folder_path):
        self.reset_state()
        self.TL = rwtools.load_pickle(folder_path+r'\TL.model')
        self.tfv = rwtools.load_pickle(folder_path+r'\tfv.model')
        self.cnt_v = rwtools.load_pickle(folder_path+r'\cnt_v.model')
        self.mtrx = scipy.sparse.load_npz(folder_path+r'\mtrx.npz')
        self.N = rwtools.load_pickle(folder_path+r'\N.model')
        self.poses = rwtools.load_pickle(folder_path+r'\poses.model')
        self.df = rwtools.load_pickle(folder_path+r'\df.model')
        self.flags = rwtools.load_pickle(folder_path+r'\flags.model')

class ResultsCompiler():
    def __init__(self):
        self.res_store = {}
        self.concls = []
        
    def add_results(self, results, concl):
        if concl not in self.res_store:
            self.concls.append(concl)
            res_dct = self._convert_to_dct(results)
        else:
            res_dct = self._combine_two_res(results, concl)
        self.res_store[concl] = res_dct
    
    def retrive_results(self, concl=None):
        if concl:
            if concl in self.res_store:
                res_dct = self.res_store[concl]
                res_list = [
                    (req, attrs['score'], attrs['alg'], attrs['pos'])
                    for req, attrs in res_dct.items()
                ]
                res_list = sorted(res_list, key=lambda x: x[1], reverse=True)
                return res_list
            else:
                return 'Conclusion was not processed!'
        else:
            res_dct = {}
            for concl in self.concls:
                dct = self.res_store[concl]
                res_list = [
                    (req, attrs['score'], attrs['alg'], attrs['pos'])
                    for req, attrs in dct.items()
                ]
                res_list = sorted(res_list, key=lambda x: x[1], reverse=True)
                res_dct[concl] = res_list
            return res_dct

    def _convert_to_dct(self, results):
        dct = {
            req:{'score':score, 'alg':alg_mark, 'pos':pos}
            for req, score, alg_mark, pos in results
        }
        return dct

    def _combine_two_res(self, results, concl):
        res_base_dct = self.res_store[concl]
        for item in results:
            req, score, alg_mark, pos = item
            if req in res_base_dct:
                res_base_dct[req]['score']+=score
                res_base_dct[req]['alg']+=alg_mark
            else:
                res_base_dct[req] = {
                    'score':score, 'alg':alg_mark, 'pos':pos
                }
        return res_base_dct
    
    def reset_state(self):
        self.res_store = {}
        self.concls = []
    
def find_acts(cnls, ind_obj, rc_obj):
    for ind, cnl in enumerate(cnls):
        cnl = cnl.strip()
        res = ind_obj.query_find_similar_acts(cnl, border=(2,3))
        if isinstance(res, str):
            print('# {: >2d}'.format(ind), res)
            continue
        rc_obj.add_results(res, cnl)

def write_it(cnls, RC):
    from writer import writer
    for ind, cnl in enumerate(cnls):
        cnl = cnl.strip()
        holder = [cnl]
        holder.append('='*150)
        for res in RC.retrive_results(cnl)[:5]:
            if isinstance(res, str):
                print('IND #', ind, res)
                holder.append('Подходящих актов не найдено!')
                writer(holder, 'cnl_{:0>3d}'.format(ind), mode='w', verbose=False)
                break
            st = '{:-<90s} || SC: {: >7.5f} || AL: {: >6s} || POS: {: >5d}'
            st = st.format(*res)
            holder.append(st)
        writer(holder, 'cnl_{:0>3d}'.format(ind), mode='w', verbose=False)

def write_it_2(cnls, RC, folder):
    for ind, cnl in enumerate(cnls, start=1):
        cnl = cnl.strip()
        holder = [cnl]
        holder.append('='*127)
        for res in RC.retrive_results(cnl)[:5]:
            if isinstance(res, str):
                print('IND #', ind, res)
                holder.append('Подходящих актов не найдено!')
                with open(folder.joinpath('вывод_{:0>3d}.txt'.format(ind)), mode='w') as f:
                    for i in holder:
                        f.write(i)
                break
            st = '{:-<95s} || Ранг: {: >7.5f}'
            st = st.format(res[0], res[1])
            holder.append(st)
        with open(folder.joinpath('вывод_{:0>3d}.txt'.format(ind)), mode='w') as f:
            for i in holder:
                f.write(i+'\n')

        
        
        



