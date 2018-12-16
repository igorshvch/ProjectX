import re

from debugger import timer


class MyReader():
    def __init__(self):
        self.date_pos = []
        self.dates = {}
        self.file_size = 0
        self.doc_pos = []
    @timer
    def find_docs(self, file, pattern_date, pattern_start, pattern_end):
        file.seek(0)
        last_position = -1
        while True:
            line = file.readline()
            current_position = file.tell()
            if re.match(pattern_date, line):
                self.date_pos.append(current_position)
                self.dates.setdefault(
                    file.readline()[:-1], []
                ).append(len(self.date_pos)-1)
                continue
            elif re.match(pattern_start, line):
                start_pos = current_position
                continue
            elif re.match(pattern_end, line):
                end_pos = current_position
                self.doc_pos.append((start_pos, end_pos))
            if last_position == current_position:
                self.file_size = round(current_position/(1024**2), 3)
                break
            else:
                last_position = current_position
    @timer
    def find_doc(self, file, index, mode='act', codec='cp1251'):
        file.seek(0)
        buffer = file.buffer
        if mode == 'act':
            start, stop = self.doc_pos[index]
            buffer.seek(start)
        elif mode == 'date':
            start, stop = self.date_pos[index:index+2]
            buffer.seek(self.date_pos[index])
        act_b = buffer.read(stop-start)
        text = act_b.decode(codec)[2:-74]
        return text