import re
import random

import debugger as dbg

@dbg.timer_with_func_name
def find_demands(corp_iter):
    demands = []
    errors = []
    for ind, doc in enumerate(corp_iter):
        if ind % 10000 == 0:
            print('Docs:', ind)
        text = doc['Текст документа']
        re_obj = re.search(
            r'\n([Уу]становил:\n.*|[Уу]становила:\n.*).*(?=\.\n)',
            text
        )
        if re_obj:
            demands.append(re_obj.group())
        else:
            errors.append(ind)
    return demands, errors

def print_rd_error(corp_iter, errors):
    def inner_f(start=0, lng=400, num=None):
        if not num:
            numb = errors[random.randint(0, len(errors)-1)]
            print(numb)
        else:
            numb = num
        print(corp_iter[numb]['Текст документа'][start:lng])
    return inner_f