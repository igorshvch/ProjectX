# -*- coding: utf-8 -*-
"""
Created on Tue Dec 11 22:28:24 2018

@author: igors
"""

import pickle
from searchapp.debuger import timer

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