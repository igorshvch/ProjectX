import pickle
import itertools
from collections import Counter

from debugger import timer

class IOPickler():
    def __init__(self, file):
        self.file = file
        self.indexer = []
    
    @timer
    def write(self, data_iterable):
        if self.file.closed:
            return 'File is closed!'
        self.file.seek(0)
        self.indexer = []
        pick = pickle.Pickler(self.file)
        for item in data_iterable:
            self.indexer.append(self.file.tell())
            pick.dump(item)
    
    def load_all_item(self, pos=0):
        if self.file.closed:
            return 'File is closed!'
        self.file.seek(pos)
        unpick = pickle.Unpickler(self.file)
        error = False
        while not error:
            try:
                item = unpick.load()
                yield item
            except:
                error = True
    
    def _load_item(self, pos):
        if self.file.closed:
            return 'File is closed!'
        self.file.seek(pos)
        unpick = pickle.Unpickler(self.file)
        return unpick.load()
    
    def append(self, item):
        if self.file.closed:
            return 'File is closed!'
        self.file.seek(self.indexer[-1], 2)
        self.indexer.append(self.file.tell())
        pick = pickle.Pickler(self.file)
        pick.dump(item)
    
    def __getitem__(self, int_num):
        try:
            pos = self.indexer[int_num]
        except IndexError:
            return 'Position is out of index'
        return self._load_item(pos)
    
