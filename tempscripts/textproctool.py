import pickle
import itertools
from collections import Counter

from debugger import timer

class IOPickler():
    def __init__(self, file):
        self.file = file
    
    @timer
    def write(self, data_iterable, **kwargs):
        if self.file.closed:
            return 'File is closed!'
        self.file.seek(0)
        pick = pickle.Pickler(self.file, **kwargs)
        for item in data_iterable:
            pick.dump(item)
    
    def load_item(self, pos=0, **kwargs):
        if self.file.closed:
            return 'File is closed!'
        self.file.seek(pos)
        unpick = pickle.Unpickler(self.file, **kwargs)
        error = False
        while not error:
            try:
                item = unpick.load()
                yield item
            except:
                error = True