import re

from textproc import texttools

def concord(text, parameters=None):
    char, char_num_min, char_num_max, dist = parameters
    pattern = (
        r'(?=(.{{{0:d}}} {1:s}{{{2:d},{3:d}}}[ ,\.].{{{4:d}}}))'\
        .format(dist, char, char_num_min, char_num_max, dist)
    )
    print(pattern)
    res = re.findall(pattern, text, flags=re.DOTALL)
    formatter = texttools.form_string_pattern(' ', 's', char_num_max)
    return [
        '  |  '.join(
            [line[:dist],
            formatter.format(line[dist+1:len(line)-dist-1]),
            line[-dist:]]
         )
         for line in res]