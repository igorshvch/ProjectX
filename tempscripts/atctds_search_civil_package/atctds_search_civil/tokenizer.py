import re
import tempfile

from .textproc import PARSER
from . import iopickler as iop

class Tokenizer():
    def __init__(self,
                 iterator,
                 stpw,
                 delim=10000,
                 temp_store=None,
                 processed=False):
        self.iterator = iterator
        self.stpw = stpw
        self.temp_store = self._store_data(temp_store)
        self.flag_process = processed
        self.delim = delim
    
    def _store_data(self, temp_store):
        speaker = '\tTokenizer:'
        if not temp_store:
            print(speaker, 'File not found! Create temporary file')
            return iop.IOPickler(tempfile.TemporaryFile())
        else:
            print(speaker, 'Using file "{}"'.format(temp_store.name))
            return iop.IOPickler(temp_store)

    def __iter__(self):
        delim = self.delim
        if not self.flag_process:
            self.process_documents()
        print('Start iteration over tokenized corpus')
        for ind, doc in enumerate(self.temp_store, start=1):
            if ind % delim == 0:
                print('\t\tDocument #', ind)
            yield doc
    
    def __getitem__(self, index):
        if self.flag_process:
            return self.temp_store[index]
        else:
            return 'Documents were not tokenized!'
    
    def __len__(self):
        if self.flag_process:
            return len(self.temp_store)
        else:
            return 'Documents were not tokenized!'

    def process_documents(self):
        print('Start tokenization')
        stpw = self.stpw
        delim = self.delim
        for ind, doc in enumerate(self.iterator, start=1):
            if ind % delim == 0:
                print('\t\tDocument #', ind)
            doc = doc.lower()
            doc = re.findall(r'\b[А-я0-9][А-я0-9-]*', doc)
            doc = [word for word in doc if word not in stpw]
            self.temp_store.append(doc)
        self.flag_process = True

class TokenizerLem(Tokenizer):
    def __init__(self,
                 iterator,
                 stpw,
                 delim=10000,
                 lem_map=None,
                 temp_store_lem=None,
                 processed=False):
        Tokenizer.__init__(self, iterator, stpw, delim, temp_store=None)
        self.temp_store_lem = self._store_lem_data1(temp_store_lem)
        self.flag_process = processed
        self.lem_map = lem_map
        if self.lem_map:
            print('\tTokenizerLem: get lem map!')
    
    def _store_lem_data1(self, temp_store_lem):
        speaker = '\tTokenizerLem:'
        if not temp_store_lem:
            print(speaker, 'File not found! Create temporary file')
            return iop.IOPickler(tempfile.TemporaryFile())
        else:
            print(speaker, 'Using file "{}"'.format(temp_store_lem.name))
            return iop.IOPickler(temp_store_lem)

    def __iter__(self):
        delim = self.delim
        if not self.flag_process:
            self.process_documents()
        print('Start iteration over lemmatized corpus')
        for ind, doc in enumerate(self.temp_store_lem, start=1):
            if ind % delim == 0:
                print('\t\tDocument #', ind)
            yield doc
    
    def __getitem__(self, index):
        if self.flag_process:
            return self.temp_store_lem[index]
        else:
            return 'Documents were not lemmatized!'
    
    def process_documents(self):
        print('Start lemmatization')
        delim = self.delim
        uniq_words = self.create_total_voc()
        if self.lem_map:
            print('\t\tGet lem map!')
            lem_map = self.lem_map
        else:
            lem_map = self.create_lem_mapping(uniq_words)
            self.lem_map = lem_map
        print('\tLemmatizing corpus!')
        for ind, doc in enumerate(self.temp_store, start=1):
            if ind % delim == 0:
                print('\t\tDocument #', ind)
            doc = [lem_map[word] for word in doc]
            self.temp_store_lem.append(doc)
        self.flag_process = True

    def create_total_voc(self, mode='alph_dgts'):
        if mode == 'alph_dgts':
            pattern = r'\b[а-я0-9][а-я0-9-]*'
        elif mode == 'alph':
            pattern = r'\b[а-я][а-я-]+'
        print('\tTokenizing corpus!')
        holder = set()
        stpw = self.stpw
        delim = self.delim
        for ind, doc in enumerate(self.iterator, start=1):
            if ind % delim == 0:
                print('\t\tDocument #', ind)
            doc = doc.lower()
            doc = re.findall(pattern, doc)
            doc = [word for word in doc if word not in stpw]
            self.temp_store.append(doc)
            doc = set(doc)
            holder.update(doc)
        print('\t\tTotal uniq tokens in corpus:', len(holder))
        return holder

    def create_lem_mapping(self, holder):
        print('\tCreating lem mapping!')
        return {word:PARSER(word) for word in holder}
    
    def extract_lem_map(self):
        return self.lem_map

class TokenizerLemBigr(TokenizerLem):
    def __init__(self,
                 iterator,
                 stpw,
                 delim=10000,
                 word_len=1,
                 lem_map=None,
                 temp_store_lem=None,
                 processed=False):
        TokenizerLem.__init__(self, iterator, stpw, delim, temp_store_lem=None)
        self.temp_store_lem = self._store_lem_data2(temp_store_lem)
        self.flag_process = processed
        self.lem_map = lem_map
        self.word_len = word_len
        if self.lem_map:
            print('\tTokenizerLemBigr: get lem map!')
    
    def _store_lem_data2(self, temp_store_lem):
        speaker = '\tTokenizerLemBigr:'
        print(speaker, 'Override TokenizerLem, using', speaker[:-1].upper())
        if not temp_store_lem:
            print(speaker, 'File not found! Create temporary file')
            return iop.IOPickler(tempfile.TemporaryFile())
        else:
            print(speaker, 'Using file "{}"'.format(temp_store_lem.name))
            return iop.IOPickler(temp_store_lem)

    def create_bigrams(self, doc):
        doc = [
            doc[i-1]+'#'+doc[i]
            for i in range(1, len(doc), 1)
        ]
        return doc

    def process_documents(self):
        counter = 0
        create_bigrams = self.create_bigrams
        print('Start bigram creation')
        delim = self.delim
        word_len=self.word_len
        uniq_words = self.create_total_voc(mode='alph')
        if self.lem_map:
            print('\t\tGet lem map!')
            lem_map = self.lem_map
        else:
            lem_map = self.create_lem_mapping(uniq_words)
            self.lem_map = lem_map
        print('\tLemmatizing corpus and creating bigrams!')
        for ind, doc in enumerate(self.temp_store, start=1):
            if ind % delim == 0:
                print('\t\tDocument #', ind)
            doc = [lem_map[word] for word in doc if len(word) > word_len]
            doc = create_bigrams(doc)
            counter+=len(doc)
            self.temp_store_lem.append(doc)
        print('\t\tTotal bigrams in corpus:', counter)
        self.flag_process = True

class TokenizerLemTrigr(TokenizerLem):
    def __init__(self,
                 iterator,
                 stpw,
                 delim=10000,
                 word_len=1,
                 lem_map=None,
                 temp_store_lem=None,
                 processed=False):
        TokenizerLem.__init__(self, iterator, stpw, delim)
        self.temp_store_lem = self._store_lem_data(temp_store_lem)
        self.flag_process = processed
        self.lem_map = lem_map
        self.word_len = word_len
        if self.lem_map:
            print('\tTokenizerLemTrigr: get lem map!')
    
    def _store_lem_data(self, temp_store_lem):
        speaker = '\tTokenizerLemTrigr:'
        if not temp_store_lem:
            print(speaker, 'File not found! Create temporary file')
            return iop.IOPickler(tempfile.TemporaryFile())
        else:
            print(speaker, 'Using file "{}"'.format(temp_store_lem.name))
            return iop.IOPickler(temp_store_lem)
    
    def create_trigrams(self, doc):
        doc = [
            doc[i-2]+'#'+doc[i-1]+'#'+doc[i]
            for i in range(2, len(doc), 1)
        ]
        return doc

    def process_documents(self):
        create_trigrams = self.create_trigrams
        print('Start trigram creation')
        delim = self.delim
        word_len=self.word_len
        uniq_words = self.create_total_voc(mode='alph')
        if self.lem_map:
            print('\t\tGet lem map!')
            lem_map = self.lem_map
        else:
            lem_map = self.create_lem_mapping(uniq_words)
            self.lem_map = lem_map
        for ind, doc in enumerate(self.temp_store, start=1):
            if ind % delim == 0:
                print('\t\tDocument #', ind)
            doc = [lem_map[word] for word in doc if len(word) > word_len]
            doc = create_trigrams(doc)
            self.temp_store_lem.append(doc)
        self.flag_process = True