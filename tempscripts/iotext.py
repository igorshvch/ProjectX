import re


class MyReader():
    def __init__(self):
        self.date_pos = []
        self.date = {}
    def find_dates(self, file, pattern):
        file.seek(0)
        last_position = -1
        while True:
            line = file.readline()
            current_position = file.tell()
            if re.match(pattern, line):
                self.date_pos.append(current_position)
                self.date.setdefault(
                    file.readline()[:-1], []
                ).append(current_position)
                continue
            if last_position == current_position:
                break
            else:
                last_position = current_position
    def find_act(self, file, index, codec='cp1251'):
        file.seek(0)
        buffer = file.buffer
        start, stop = self.date_pos[index:index+2]
        buffer.seek(self.date_pos[index])
        act_b = buffer.read(stop-start)
        text = act_b.decode(codec)
        return text