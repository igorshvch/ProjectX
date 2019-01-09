#https://stackoverflow.com/questions/9708902/in-practice-what-are-the-main-uses-for-the-new-yield-from-syntax-in-python-3
import re
import random
from datetime import date

from textproc import rwtools
from debugger import timer


class MyReader():
    def __init__(self, file):
        self.file = file
        self.file_size = file.seek(0, 2)
        self.dates_to_poses = {} #store dates positions by date {date : [pos1, pos2]}
        self.dates_to_docs = {} #store docs positions by date {date: [pos1, pos2]}
        self.dates_poses = []
        self.docs_poses = []
    @timer
    def find_docs(self,
                  pattern_date,
                  pattern_doc_start,
                  pattern_doc_end,
                  codec='cp1251'):
        #Patterns: (r'Когда получен\n', r'Текст документа\n', r'-{66}')
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
    @timer
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
            return None
        docs_poses = self.dates_to_docs[d]
        print(
            'There are {: >3d}'.format(len(docs_poses)),
            'documents by date {}'.format(str(d))
        )
        buffer = self.file.buffer
        for pose in docs_poses:
            start, stop = pose
            buffer.seek(start)
            doc_b = buffer.read(stop-start)
            text = doc_b.decode(codec)[2:-74]
            yield text
    
    def print_stats(self):
        print(self.file.name)
        for key in sorted(self.dates_to_poses.keys()):
            docs_quant = len(self.dates_to_poses[key])
            print('{: <11s} : {: >3d} docs'.format(str(key), docs_quant))
    
    def print_stats_by_date(self, year, month, day):
        d = date(year, month, day)
        if d not in self.dates_to_poses:
            raise KeyError('No docs by date {}',format(str(d)))
        docs_quant = len(self.dates_to_poses[d])
        print('{: <11s} : {: >4d} docs'.format(str(d), docs_quant))

class TextInfoCollector():
    def __init__(self, folder):
        self.folder = folder
        self.readers = {}
    @timer
    def process_files(self):
        f_paths = rwtools.collect_exist_files(self.folder, suffix='.txt')
        for path in f_paths:
            self.readers[path.stem] = MyReader(open(path, mode='r'))
            self.readers[path.stem].find_docs(
                r'Когда получен\r', r'Текст документа\r', r'-{66}'
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

class MyReader_iter():
    def __init__(self, file):
        self.file = file
        self.file_size = file.seek(0, 2)
        self.state = 0
        self.date_pos = []
        self.dates = {}
        self.doc_pos = []
    def find_docs(self, pattern_date, pattern_start, pattern_end):
        pid = random.randint(1000,9999)
        self.file.seek(0)
        last_position = -1
        while True:
            line = self.file.readline()
            current_position = self.file.tell()
            self.state = current_position
            if last_position == current_position:
                break
            else:
                last_position = current_position
            if re.match(pattern_date, line):
                self.date_pos.append((pid, current_position))
                self.dates.setdefault(
                    self.file.readline()[:-1], []
                ).append(len(self.date_pos)-1)
                yield 0
            elif re.match(pattern_start, line):
                start_pos = current_position
                yield 0
            elif re.match(pattern_end, line):
                end_pos = current_position
                self.doc_pos.append((pid, start_pos, end_pos))
                yield 0
            else:
                continue
    def find_doc(self, index, mode='act', codec='cp1251'):
        self.file.seek(0)
        buffer = self.file.buffer
        if mode == 'act':
            start, stop = self.doc_pos[index]
            buffer.seek(start)
        elif mode == 'date':
            start, stop = self.date_pos[index:index+2]
            buffer.seek(self.date_pos[index])
        act_b = buffer.read(stop-start)
        text = act_b.decode(codec)[2:-74]
        return text