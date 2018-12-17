import re
import random

from debugger import timer


class MyReader():
    def __init__(self, file):
        self.__file = file
        self.file_size = file.seek(0, 2)
        self.__state = 0
        self.date_pos = []
        self.dates = {}
        self.doc_pos = []
    @timer
    def find_docs(self, pattern_date, pattern_start, pattern_end):
        #Patterns: (r'Когда получен\n', r'Текст документа\n', r'-{66}')
        self.__file.seek(0)
        last_position = -1
        while True:
            line = self.__file.readline()
            current_position = self.__file.tell()
            self.__state = current_position/self.file_size
            if re.match(pattern_date, line):
                self.date_pos.append(current_position)
                self.dates.setdefault(
                    self.__file.readline()[:-1], []
                ).append(len(self.date_pos)-1)
                continue
            elif re.match(pattern_start, line):
                start_pos = current_position
                continue
            elif re.match(pattern_end, line):
                end_pos = current_position
                self.doc_pos.append((start_pos, end_pos))
            if last_position == current_position:
                break
            else:
                last_position = current_position
    @timer
    def find_doc(self, index, mode='act', codec='cp1251'):
        self.__file.seek(0)
        buffer = self.__file.buffer
        if mode == 'act':
            start, stop = self.doc_pos[index]
            buffer.seek(start)
        elif mode == 'date':
            start, stop = self.date_pos[index:index+2]
            buffer.seek(self.date_pos[index])
        act_b = buffer.read(stop-start)
        text = act_b.decode(codec)[2:-74]
        return text

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