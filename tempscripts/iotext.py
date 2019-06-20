#https://stackoverflow.com/questions/9708902/in-practice-what-are-the-main-uses-for-the-new-yield-from-syntax-in-python-3
import re
import random
import tempfile
from datetime import date
from typing import Sequence, List, Dict, Tuple

from textproc import rwtools, PARSER
from debugger import timer, timer_message
from tempscripts import textproctool as tpt


class MyReaderPre():
    def __init__(self, file):
        self.file = file
        self.file_size = file.seek(0, 2)
        self.docs_poses = []
    
    def __len__(self):
        if self.docs_poses:
            return len(self.docs_poses)

    def __iter__(self):
        for i in range(len(self)):
            yield self.find_doc(i)
    
    def __getitem__(self, index):
        return self.find_doc(index)

    def find_docs(self,
                  pattern_doc_end,
                  codec='cp1251'):
        #Pattern: r'-{66}'
        buffer = self.file.buffer
        buffer.seek(0)
        last_position = start_pos = 0
        while True:
            line = buffer.readline().decode(codec)
            current_position = buffer.tell()
            if re.match(pattern_doc_end, line):
                end_pos = current_position
                self.docs_poses.append((start_pos, end_pos))
                start_pos = end_pos
                continue
            if last_position == current_position:
                break
            else:
                last_position = current_position

    def find_doc(self, index, codec='cp1251'):
        buffer = self.file.buffer
        start, stop = self.docs_poses[index]
        buffer.seek(start)
        doc_b = buffer.read(stop-start)
        text = doc_b.decode(codec)[2:-74]
        return text

class MyReaderEndDate(MyReaderPre):
    def __init__(self, file):
        MyReaderPre.__init__(self, file)
        #store dates positions by date {date : [pos1, pos2]}
        #for code analysis puprose
        self.dates_to_poses = {}
        #store docs positions by date {date: [(p1s, p1e), (p2s, p2e)]}
        self.dates_to_docs = {}
        self.dates_poses = []

    def find_docs(self,
                  pattern_date=r'Когда получен[\n\r]{1,2}',
                  pattern_doc_start=r'Текст документа[\n\r]{1,2}',
                  pattern_doc_end=r'-{66}',
                  codec='cp1251'):
        #Patterns 1: (r'Когда получен\n', r'Текст документа\n', r'-{66}')
        #Patterns 2: (r'Когда получен[\n\r]{1,2}', r'Текст документа[\n\r]{1,2}', r'-{66}')
        buffer = self.file.buffer
        buffer.seek(0)
        last_position = -1
        while True:
            line = buffer.readline().decode(codec)
            current_position = buffer.tell()
            if re.match(pattern_date, line):
                d = buffer.readline().decode(codec)[:-1].split('.')
                d = date(int(d[2]), int(d[1]), int(d[0]))
                self.dates_to_poses.setdefault(d, []).append(current_position)
                self.dates_poses.append(current_position)
                continue
            elif re.match(pattern_doc_start, line):
                start_pos = current_position
                continue
            elif re.match(pattern_doc_end, line):
                end_pos = current_position
                self.dates_to_docs.setdefault(d, []).append((start_pos, end_pos))
                self.docs_poses.append((start_pos, end_pos))
            if last_position == current_position:
                break
            else:
                last_position = current_position

    def find_doc(self, index, codec='cp1251', show_date=False):
        buffer = self.file.buffer
        start, stop = self.docs_poses[index]
        buffer.seek(start)
        doc_b = buffer.read(stop-start)
        text = doc_b.decode(codec)[2:-74]
        if show_date:
            self.file.seek(self.dates_poses[index])
            d = self.file.readline()
            text = d + text
        return text

    def find_docs_by_date(self, year, month, day, codec='cp1251'):
        d = date(year, month, day)
        if d not in self.dates_to_docs:
            yield ''
        doc_poses = self.dates_to_docs[d]
        print(
            'There are {: >3d}'.format(len(doc_poses)),
            'documents by date {}'.format(str(d))
        )
        buffer = self.file.buffer
        for pose in doc_poses:
            start, stop = pose
            buffer.seek(start)
            doc_b = buffer.read(stop-start)
            text = doc_b.decode(codec)[2:-74]
            yield text
    
    def print_stats(self):
        print('-'*22)
        print('Path to file:')
        print(self.file.name)
        print('-'*22)
        counter = 0
        for key in sorted(self.dates_to_poses.keys()):
            docs_quant = len(self.dates_to_poses[key])
            counter += docs_quant
            print('{: <11s} : {: >3d} docs'.format(str(key), docs_quant))
        print('-'*22)
        print('Docs in total :', counter)
        print('-'*22)
    
    def print_stats_by_date(self, year, month, day):
        d = date(year, month, day)
        if d not in self.dates_to_poses:
            raise KeyError('No docs by date {}',format(str(d)))
        docs_quant = len(self.dates_to_poses[d])
        print('{: <11s} : {: >4d} docs'.format(str(d), docs_quant))


class TextInfoCollectorPre():
    def __init__(self, folder):
        self.folder = folder
        self.readers = {}
        self.docs_poses = {}
        self.dates_range = []
    
    def __len__(self):
        return sum(len(reader) for reader in self.readers.values())
    
    def __iter__(self):
        for key in sorted(self.readers.keys()):
            yield from self.readers[key]
    
    def __getitem__(self, index):
        key, pos = self.docs_poses[index]
        return self.readers[key].find_doc(pos)
    
    @timer
    def process_files(self):
        dates_range = []
        f_paths = rwtools.collect_exist_files(self.folder, suffix='.txt')
        for path in f_paths:
            self.readers[path.stem] = MyReaderEndDate(
                open(path, mode='r')
            )
            self.readers[path.stem].find_docs(
                r'Когда получен\r', r'Текст документа\r', r'-{66}'
            )
            dates_range.append(
                min(self.readers[path.stem].dates_to_poses.keys())
            )
            dates_range.append(
                max(self.readers[path.stem].dates_to_poses.keys())
            )
        counter = 0
        for key in self.readers:
            for j in range(len(self.readers[key])):
                self.docs_poses[counter] = (key, j)
                counter += 1
        minimum = min(dates_range)
        maximum = max(dates_range)
        self.dates_range.append(minimum)
        self.dates_range.append(maximum)
    
    def find_docs_by_date(self, year, month, day):
        for key in sorted(self.readers.keys()):
            yield from self.readers[key].find_docs_by_date(year, month, day)

class MyReader(MyReaderEndDate):
    def __init__(self, patterns_file, *args):
        MyReaderEndDate.__init__(self, *args)
        self.patterns = self._unpack_patterns_from_file(patterns_file)
        #store docs positions by date {date: [pos1, pos2]}
        self.dates_to_docs = {}
        #store docs positions by classes {class: [pos1, pos2]}
        self.classes_to_poses = {}
    
    def _unpack_patterns_from_file(self, file):
        file.seek(0)
        text = file.read().strip(' \n')
        spl = text.split('\n')
        return {i:pattern for i, pattern in enumerate(spl)}

    def _document_processor(self,
                            buffer, 
                            start_position,
                            pattern_doc_end,
                            codec='cp1251'):
        patterns = self.patterns
        length = len(patterns)
        flags = {i:True for i in range(length)}
        classlabels = set()
        buffer.seek(start_position)
        while True:
            line = buffer.readline().decode(codec)
            current_position = buffer.tell()
            if re.match(pattern_doc_end, line):
                return current_position, classlabels
            else:
                for i in range(length):
                    if flags[i] and re.search(patterns[i], line):
                        classlabels.add(i)
                        flags[i] = False
    
    def _labels_to_classes(self, labels):
        class_marks = []
        if 5 in labels or 7 in labels:
            class_marks.append('НДС')
        if 4 in labels:
            class_marks.append('НП')
        if 8 in labels or 6 in labels or {2,3} <= labels:
            class_marks.append('НДФЛ_СВ')
        if 9 in labels or {0,1} <= labels:
            class_marks.append('Ч1_НК')
        if class_marks:
            return class_marks
        else:
            return ('unarranged',)

    @timer
    def find_docs(self,
                  pattern_date,
                  pattern_doc_start,
                  pattern_doc_end,
                  codec='cp1251'):
        #Patterns 1: (r'Когда получен\n', r'Текст документа\n', r'-{66}')
        #Patterns 2: (r'Когда получен[\n\r]{1,2}', r'Текст документа[\n\r]{1,2}', r'-{66}')
        buffer = self.file.buffer
        buffer.seek(0)
        last_position = -1
        counter = 0
        while True:
            line = buffer.readline().decode(codec)
            current_position = buffer.tell()
            if re.match(pattern_date, line):
                d = buffer.readline().decode(codec)[:-1].split('.')
                d = date(int(d[2]), int(d[1]), int(d[0]))
                self.dates_to_poses.setdefault(d, []).append(current_position)
                self.dates_poses.append(current_position)
                continue
            elif re.match(pattern_doc_start, line):
                counter += 1
                start_pos = current_position
                end_pos, labels = self._document_processor(
                    buffer, start_pos, pattern_doc_end, codec=codec
                )
                classes_marks = self._labels_to_classes(labels)
                current_doc_num = len(self.docs_poses)
                for mark in classes_marks:
                    self.classes_to_poses.setdefault(mark, [])\
                    .append(current_doc_num)
                self.dates_to_docs.setdefault(d, []).append(current_doc_num)
                self.docs_poses.append((start_pos, end_pos))
                continue
            if last_position == current_position:
                break
            else:
                last_position = current_position
    
    def find_docs_by_date(self, year, month, day, codec='cp1251'):
        d = date(year, month, day)
        if d not in self.dates_to_docs:
            return None
        doc_poses = self.docs_poses[self.dates_to_docs[d]]
        print(
            'There are {: >3d}'.format(len(doc_poses)),
            'documents by date {}'.format(str(d))
        )
        buffer = self.file.buffer
        for pose in doc_poses:
            start, stop = pose
            buffer.seek(start)
            doc_b = buffer.read(stop-start)
            text = doc_b.decode(codec)[2:-74]
            yield text
    
    def find_relevant_docs_by_date(self, docs_class_key, year, month, day):
        d = date(year, month, day)
        if d not in self.dates_to_docs:
            raise 'Incorrect date'
        if docs_class_key not in self.classes_to_poses:
            raise 'Inccorect docs group ID'
        test_set = set(self.dates_to_docs[d])
        for ind in self.classes_to_poses[docs_class_key]:
            if ind in test_set:
                yield self.find_doc(ind)
    
    def find_relevant_docs_after_date(self, docs_class_key, year, month, day):
        d = date(year, month, day)
        if docs_class_key not in self.classes_to_poses:
            return 'Inccorect docs group ID'
        test_set = []
        for key_date in sorted(self.dates_to_docs.keys()):
            if d <= key_date:
                test_set.extend(self.dates_to_docs[key_date])
        test_set = set(test_set)
        for ind in self.classes_to_poses[docs_class_key]:
            if ind in test_set:
                yield self.find_doc(ind) 


class MyReader_testing(MyReader):
    def __init__(self, *args):
        MyReader.__init__(self, *args)
    
    def show_class_info(self):
        if not self.classes_to_poses:
            return 'Documents werre not arranged'
        for key in self.classes_to_poses:
            print (key, len(self.classes_to_poses[key]))
    
    def find_patterns_in_lines(self, indexes: Sequence[int]):
        '''
        Search lines for patterns which are used in MyReader._document_processor().
        To get lines document with specified index is used
        Example of output:
        ======>>0147==============================
        (29, 'налог[а-я]*')
        (34, 'налог[а-я]*')
        (34, 'взнос[а-я]*')
        (34, 'на доходы физических лиц')
        (36, 'взнос[а-я]*')
        '''
        holder = []
        for doc_ind in indexes:
            holder.append('='*10 + str(doc_ind) + '='*10)
            text = self.find_doc(doc_ind, show_date=True)
            for ind, line in enumerate(text.split('\n')):
                for key in self.patterns:
                    if re.search(self.patterns[key], line):
                        holder.append((ind, self.patterns[key]))
        return holder


class TextInfoCollector():
    def __init__(self, folder, path_to_patterns):
        self.path_to_patterns = path_to_patterns
        self.folder = folder
        self.readers = {}
    @timer
    def process_files(self):
        f_paths = rwtools.collect_exist_files(self.folder, suffix='.txt')
        for path in f_paths:
            self.readers[path.stem] = MyReader(
                open(self.path_to_patterns, mode='r'),
                open(path, mode='r')
            )
            self.readers[path.stem].find_docs(
                r'Когда получен\r', r'Текст документа\r', r'-{66}'
            )
    
    def find_relevant_docs_by_date(self, docs_class_key, year, month, day):
        for key in sorted(self.readers.keys()):
            yield from self.readers[key].find_relevant_docs_after_date(
                docs_class_key, year, month, day
            )
    
    def find_docs_by_date(self, year, month, day):
        for key in sorted(self.readers.keys()):
            yield from self.readers[key].find_docs_by_date(year, month, day)

    def print_stats_global(self):
        for key in self.readers.keys():
            self.readers[key].print_stats()
    
    def inspect(self, year, month, day):
        d = date(year, month, day)
        print('PRINT FILE SIZES')
        for key in self.readers.keys():
            print(key, '===', self.readers[key].file_size)
        print('PRINT DATE POSES')
        for key in self.readers.keys():
            if d in self.readers[key].dates_to_poses:
                print(key, '===', self.readers[key].dates_to_poses[d])
        print('PRINT DOC COORDS')
        for key in self.readers.keys():
            if d in self.readers[key].dates_to_docs:
                print(key, '===', self.readers[key].dates_to_docs[d])



def test_find_positions_by_pattern(folder, pattern):
    '''
    Testing.
    Find positons of text sequences corresponding
    to the pattern passed as argument
    '''
    holder = []
    last_pos = -1
    fp = rwtools.collect_exist_files(folder, suffix='.txt')
    for path in fp:
        print(path.name)
        holder.append(str(fp))
        with open(path, mode='r') as file:
            while True:
                line = file.readline()
                cur_pos = file.tell()
                if re.match(pattern, line):
                    holder.append(cur_pos)
                if last_pos ==  cur_pos:
                    break
                else:
                    last_pos = cur_pos
    return holder

def test_simple_text_gen(words_num, alph=1040):
    '''
    Testing.
    Generate semi-text sequences for further indexing tests
    '''
    alph = [chr(i) for i in range(alph, alph+32)]
    res = []
    while words_num:
        length = random.randint(1, 20)
        res.append(''.join(random.sample(alph, k=length)))
        words_num -= 1
    return res

@timer
def test_indexer(docs, vocab=None, tokenizer=None):
    '''
    Testing.
    Create primitive inverted index table on passed iterable with tokened docs
    '''
    if vocab:
        inner_voc = vocab
    else:
        inner_voc = dict()
    for ind, doc in enumerate(docs):
        if tokenizer:
            doc = tokenizer(doc)
        for token in set(doc):
            inner_voc.setdefault(token, []).append(ind)
    return inner_voc

def test_word_expand(word, morph=None):
    '''
    Query word expander. Use pymorphy2 'MorphAnalyzer' instance

    -> In[0]: test_word_expand('взносы')
    -> Out[79]: 
    -> ['взнос',
        'взноса',
        ...
        'взносах'] 
    '''
    w = morph.parse(word)[0]
    res = [i[0] for i in w.lexeme]
    return res


class Tokenizer():
    def __init__(self, iterator, stpw, delim=10000):
        self.iterator = iterator
        self.stpw = stpw
        self.temp_store = tpt.IOPickler(tempfile.TemporaryFile())
        self.flag_process = False
        self.delim = delim
    
    def __iter__(self):
        delim = self.delim
        if not self.flag_process:
            self.process_documents()
        print('Start iteration over tokenized corpus')
        for ind, doc in enumerate(self.temp_store, start=1):
            if ind % delim == 0:
                print('\tDocument #', ind)
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
                print('\tDocument #', ind)
            doc = doc.lower()
            doc = re.findall(r'\b[А-я0-9][А-я0-9-]*', doc)
            doc = [word for word in doc if word not in stpw]
            self.temp_store.append(doc)
        self.flag_process = True

class TokenizerLem(Tokenizer):
    def __init__(self, iterator, stpw, delim=10000, lem_map=None):
        Tokenizer.__init__(self, iterator, stpw, delim)
        self.temp_store_lem = tpt.IOPickler(tempfile.TemporaryFile())
        self.lem_map = lem_map
        if self.lem_map:
            print('\t\tTokenizerLem: get lem map!')
    
    def __iter__(self):
        delim = self.delim
        if not self.flag_process:
            self.process_documents()
        print('Start iteration over lemmatized corpus')
        for ind, doc in enumerate(self.temp_store_lem, start=1):
            if ind % delim == 0:
                print('\tDocument #', ind)
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
            print('\tGet lem map!')
            lem_map = self.lem_map
        else:
            lem_map = self.create_lem_mapping(uniq_words)
        for ind, doc in enumerate(self.temp_store, start=1):
            if ind % delim == 0:
                print('Document #', ind)
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
                print('\tDocument #', ind)
            doc = doc.lower()
            doc = re.findall(pattern, doc)
            doc = [word for word in doc if word not in stpw]
            self.temp_store.append(doc)
            doc = set(doc)
            holder.update(doc)
        print('\t\tTotal uniq tokens in corpus:', len(holder))
        return holder

    def create_lem_mapping(self, holder):
        print('\tCreateing lem mapping!')
        return {word:PARSER(word) for word in holder}

class TokenizerLemBigr(TokenizerLem):
    def __init__(self, iterator, stpw, delim=10000, word_len=1, lem_map=None):
        TokenizerLem.__init__(self, iterator, stpw, delim)
        self.temp_store_lem = tpt.IOPickler(tempfile.TemporaryFile())
        self.lem_map = lem_map
        self.word_len = word_len
        if self.lem_map:
            print('\t\tTokenizerLemBigr: get lem map!')
    
    def create_bigrams(self, doc):
        doc = [
            doc[i-1]+'#'+doc[i]
            for i in range(1, len(doc), 1)
        ]
        return doc

    def process_documents(self):
        create_bigrams = self.create_bigrams
        print('Start bigram creation')
        delim = self.delim
        word_len=self.word_len
        uniq_words = self.create_total_voc(mode='alph')
        if self.lem_map:
            print('\tGet lem map!')
            lem_map = self.lem_map
        else:
            lem_map = self.create_lem_mapping(uniq_words)
        for ind, doc in enumerate(self.temp_store, start=1):
            if ind % delim == 0:
                print('Document #', ind)
            doc = [lem_map[word] for word in doc if len(word) > word_len]
            doc = create_bigrams(doc)
            self.temp_store_lem.append(doc)
        self.flag_process = True

class TokenizerLemTrigr(TokenizerLem):
    def __init__(self, iterator, stpw, delim=10000, word_len=1, lem_map=None):
        TokenizerLem.__init__(self, iterator, stpw, delim)
        self.temp_store_lem = tpt.IOPickler(tempfile.TemporaryFile())
        self.lem_map = lem_map
        self.word_len = word_len
        if self.lem_map:
            print('\t\tTokenizerLemTrigr: get lem map!')
    
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
            print('\tGet lem map!')
            lem_map = self.lem_map
        else:
            lem_map = self.create_lem_mapping(uniq_words)
        for ind, doc in enumerate(self.temp_store, start=1):
            if ind % delim == 0:
                print('Document #', ind)
            doc = [lem_map[word] for word in doc if len(word) > word_len]
            doc = create_trigrams(doc)
            self.temp_store_lem.append(doc)
        self.flag_process = True
