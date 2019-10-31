import re

from textproc import rwtools

def code_count_lines(folder, suffix='.py', encoding='utf'):
    fp = rwtools.collect_exist_files(folder, suffix=suffix)
    counter = 0
    for i in fp:
        try:
            with open(i, mode='r', encoding=encoding) as f:
                code = f.read()
            counter += len(code.split('\n'))
        except:
            print(i.name)
    return '{: >5d} lines in {: >3d} files'.format(counter, len(fp))

def code_count_lines2(folder, suffix='.py', encoding='utf', delim='\n'):
    fp = rwtools.collect_exist_files(folder, suffix=suffix)
    counter_code_lines = 0
    counter_all_lines = 0
    counter_blank_lines = 0
    counter_comment_lines = 0
    for i in fp:
        try:
            with open(i, mode='r', encoding=encoding) as f:
                code = f.read()
        except:
            print(i.name)
            continue
        code = code.split('\n')
        for line in code:
            line
            if not line:
                counter_blank_lines += 1
            else:
                line = line.strip(' \t')
                if not line:
                    counter_blank_lines += 1
                elif line[0] == '#':
                    counter_comment_lines += 1
                else:
                    counter_code_lines += 1
        counter_all_lines = (
            counter_blank_lines
            + counter_code_lines
            + counter_comment_lines
        )   
    return (
        delim.join(
            (
                'Total lines: {: >6d} in {: >3d} files:'.format(
                    counter_all_lines, len(fp)
                ),
                '1) code lines:    {: >6d}'.format(counter_code_lines),
                '2) comment lines: {: >6d}'.format(counter_comment_lines),
                '3) blank lines:   {: >6d}'.format(counter_blank_lines)
            )
        )
    )