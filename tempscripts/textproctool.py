import pickle
import itertools
from collection import Counter

class Processor(pickle.Pickler):
    def __init__(self, input_paths, output_path):
        pickle.Pickler.__init__(self, *args, **kwargs)
        self.input_paths = input_paths
        self.output_paths = output_paths