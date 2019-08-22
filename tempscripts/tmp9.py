import re
from datetime import date

def read_text(filepath, patterns):
    with open(filepath, mode='r') as lines_iterator:
        text = next(lines_iterator).strip()
        splited = text.split('\n\n')
        store = []
        for excerpt in splited:
            lines = (line for line in excerpt.split('\n'))
            local = []
            for line in lines:
                for pattern in patterns:
                    if pattern == line:
                        local.append(next(lines))
                        break
            store.append(local)
    return store


class MyReader():
    '''
    Class defines interface to file's contents.
    It provides methodes to iterate over documents
    which were previously write to one .txt file.
    Delimiters between documents can be set manually
    '''
    def __init__(self, file, patterns=None, codec='cp1251'):
        self.file_size = file.seek(0, 2)
        file.seek(0)
        self.file = file
        self.codec = codec
        self.patterns = patterns # iterable with strings
        self.store = None #dict with posese
    
    def __len__(self):
        if self.store:
            for key in self.store:
                return len(self.store[key])

    def __iter__(self):
        for i in range(len(self)):
            yield self.find_doc(i)
    
    def __getitem__(self, index):
        return self.find_doc(index)
    
    def find_docs(self):
        end_mark = self.file.seek(0,2)
        self.file.seek(0)
        buffer = self.file.buffer
        bpatterns = set((bytes(p, encoding=self.codec) for p in self.patterns))
        store = {p:[] for p in bpatterns}
        for bline in buffer:
            position = buffer.tell()
            if position == end_mark:
                break
            for bpattern in bpatterns:
                if re.match(bpattern, bline):
                    store[bpattern].append(position)
                    break
        new_store = {
            p:store[bytes(p, encoding=self.codec)]
            for p in self.patterns
        }
        self.store = new_store

    def find_doc(self, index):
        if index > len(self)-1:
            raise IndexError()
        store = self.store
        poses = sorted([store[key][index] for key in store])
        buffer = self.file.buffer
        start = poses[-2]
        stop = poses[-1]
        buffer.seek(start)
        doc_b = buffer.read(stop-start)
        text = doc_b.decode(self.codec)[2:-74]
        return text
















class MyReaderEndDate():
    '''
    Sub class which defines specific method to find
    court desicions previously writen to single .txt file.
    It is implied that desicions are separated by 
    blocks of metainformation such as dates of loading
    to 'K+' base
    '''
    def __init__(self, file, patterns=None, codec='cp1251'):
        self.file_size = file.seek(0, 2)
        file.seek(0)
        self.file = file
        self.codec = codec
        self.patterns = patterns # iterable with strings
        self.store = None #dict with posese
        #Inhereted attribute: self.docs_poses
        #it stores docs positions: [(p1s, p1e), (p2s, p2e), ...]
        self.dates_poses = [] # [p1, p2, ...]
        self.dates_to_poses = {} #store dates positions {date : [ind1, ind2]}
        self.dates_to_docs = {} #store docs positions by date {date: [ind1, ind2, ...]}
        #Patterns1: (r'Когда получен\n', r'Текст документа\n', r'-{66}')
        #Patterns2: (r'Когда получен[\n\r]{1,2}', r'Текст документа[\n\r]{1,2}', r'-{66}')
    
    def __len__(self):
        if self.store:
            for key in self.store:
                return len(self.store[key])

    def __iter__(self):
        for i in range(len(self)):
            yield self.find_doc(i)
    
    def __getitem__(self, index):
        return self.find_doc(index)

    def find_docs(self,
                  pattern_date=r'Когда получен[\n\r]{1,2}',
                  pattern_doc_start=r'Текст документа[\n\r]{1,2}',
                  pattern_doc_end=r'-{66}',
                  codec='cp1251'):
        docs_poses = []
        dates_poses = []
        dates_to_docs = {}
        dates_to_poses = {}
        buffer = self.file.buffer
        buffer.seek(0)
        last_position = -1
        pd = bytes(pattern_date, encoding=codec)
        pds = bytes(pattern_doc_start, encoding=codec)
        pde = bytes(pattern_doc_end, encoding=codec)
        bdot = bytes('.', encoding=codec)
        while True:
            line = buffer.readline()
            current_position = buffer.tell()
            if re.match(pd, line):
                d = buffer.readline()[:-1].split(bdot)
                d = date(int(d[2]), int(d[1]), int(d[0]))
                dates_to_poses.setdefault(d, []).append(
                    len(dates_poses)
                )
                dates_poses.append(current_position)
                continue
            elif re.match(pds, line):
                start_pos = current_position
                continue
            elif re.match(pde, line):
                end_pos = current_position
                dates_to_docs.setdefault(d, []).append(
                    len(docs_poses)
                )
                docs_poses.append((start_pos, end_pos))
            if last_position == current_position:
                break
            else:
                last_position = current_position
        self.docs_poses = docs_poses
        self.dates_poses = dates_poses
        self.dates_to_docs = dates_to_docs
        self.dates_to_poses = dates_to_poses
    
    def find_docs_new(self,
                      patterns=(
                          'Когда получен[\\n\\r]{1,2}',
                          'Текст документа[\\n\\r]{1,2}',
                          '-{66}'
                          ),
                      codec='cp1251'):
        end_mark = self.file.seek(0,2)
        self.file.seek(0)
        buffer = self.file.buffer
        bpatterns = set((bytes(p, encoding=codec) for p in patterns))
        store = {p:[] for p in bpatterns}
        for bline in buffer:
            position = buffer.tell()
            if position == end_mark:
                break
            for bpattern in bpatterns:
                if re.match(bpattern, bline):
                    store[bpattern].append(position)
                    break
        new_store = {p: store[bytes(p, encoding=codec)] for p in patterns}
        self.store = new_store

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

    def find_docs_by_date(self, date_obj, codec='cp1251'):
        if date_obj not in self.dates_to_docs:
            raise KeyError('No acts to date {}'.format(date_obj))
        doc_poses = self.docs_poses
        doc_indices = self.dates_to_docs[date_obj]
        print(
            'There are {: >3d}'.format(len(doc_indices)),
            'documents by date {}'.format(date_obj)
        )
        buffer = self.file.buffer
        for index in doc_indices:
            start, stop = doc_poses[index]
            buffer.seek(start)
            doc_b = buffer.read(stop-start)
            text = doc_b.decode(codec)[2:-74]
            yield text
    
    def find_docs_after_date(self, date_obj):
        doc_indices = []
        for key_date in sorted(self.dates_to_docs.keys()):
            if date_obj <= key_date:
                doc_indices += self.dates_to_docs[key_date]
        print(
            'There are {: >3d}'.format(len(doc_indices)),
            'documents after date {}'.format(date_obj)
        )
        for index in doc_indices:
            yield self.find_doc(index)
    
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
    
    def print_stats_by_date(self, date_obj):
        if date_obj not in self.dates_to_poses:
            raise KeyError('No docs by date {}',format(date_obj))
        docs_quant = len(self.dates_to_poses[date_obj])
        print('{: <11s} : {: >4d} docs'.format(str(date_obj), docs_quant))