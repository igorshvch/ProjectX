import pickle
import functools
import math
from collections import Counter

from sklearn.feature_extraction.text import TfidfVectorizer

from debugger import timer
from textproc.normalizer import TokLem

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

##################################################

def flags_changer(key):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            args[0].flags[key] = True
            return func(*args, **kwargs)
        return wrapper
    return decorator

class Indexer():
    def __init__(self, lem_map, stpw):
        self.lem_map = lem_map
        self.stpw = stpw
        self.TL = None
        self.tfv = None
        self.mtrx = None
        self.df_dct = {}
        self.flags ={
            'tfidf' : False,
            'tokenizer' : False,
            'tfidfmatrix' : False
        }
    
    def _reset_flags(self):
        self.flags = {key:False for key in self.flags}

    @flags_changer('tokenizer')
    def init_tokenizer(self):
        self.TL = TokLem(self.lem_map, self.stpw)
    
    @flags_changer('tfidf')
    def init_tfv(self, token_pattern=r'(?u)\b\w\w+\b'):
        self.tfv = TfidfVectorizer(
            tokenizer=self.TL,
            token_pattern=token_pattern
        )
    
    @flags_changer('tfidfmatrix')
    def init_tfidf_table(self, doc_iter):
        if not self.flags['tfidf']:
            return 'Tfidf Vectorizer is not initialized'
        self.mtrx = self.tfv.fit_transform(doc_iter)
    
    def estimate_tfidf(self, text_string):
        if not self.flags['tfidfmatrix']:
            return 'Tfidf indicies are not estimated'
        return self.tfv.transform([text_string])
    
    def create_pos_index(self):
        if not self.flags['tfidfmatrix']:
            return 'Tfidf indicies are not estimated'
        self.poses = {ind:word for word,ind in self.tfv.vocabulary_.items()}
    
    def count_docfreq(self, word):
        if not self.flags['tfidfmatrix']:
            return 'Tfidf indicies are not estimated'
        pos = self.tfv.vocabulary_.get(word, None)
        if not pos:
            return 'Word is not in vocabulary!'
        vect = self.mtrx[:,pos]
        vect = vect.toarray().flatten()
        df = sum(1 for i in vect if i)
        self.df_dct[word] = df
        print('{:-<50s} : df : {:.>5d}'.format(word, df))


        
        
        



