import re
import csv
from datetime import date

import iopickler as iop


def string_to_date(string):
    res_set = set()
    if ',' in string:
        dates = string.split(',')
        for item in dates:
            parts = item.split('.')
            ddate = date(int(parts[2]), int(parts[1]), int(parts[0]))
            res_set.add(ddate)
    else:
        parts = string.split('.')
        ddate = date(int(parts[2]), int(parts[1]), int(parts[0]))
        res_set.add(ddate)
    return res_set

data_trans_funcs = {
    'comas_to_newlines': lambda x: re.subn(r',(?=[\w\n-])', '\n', x)[0],
    'find_act_content': lambda x: re.search(
        r'(?<=\bустановил\n).*(?=\bПредседательствующий\n)',
        x
    ).group(),
    'string_to_date': lambda x: string_to_date(x),
    'separate_act_ids': lambda x: set(x.split(',')),
    'court': lambda x: x.split('_')[0]
}

def custom_processor_for_ConsPlus_data(dct):
    text = dct['Текст документа']
    comas_to_newlines = data_trans_funcs['comas_to_newlines'](text)
    dct['Текст документа'] = comas_to_newlines
    try:
        content = data_trans_funcs['find_act_content'](comas_to_newlines)
    except:
        content = None
    dct['Содержание'] = content
    date_loading = dct['Когда получен']
    dct['Когда получен'] = data_trans_funcs['string_to_date'](date_loading)
    date_issue = dct['Дата']
    dct['Дата'] = None ########




    cut_edges = reg_exp_funcs['search'](comas_to_newlines)
    dct[key_to_transform] = comas_to_newlines
    if cut_edges:
        dct['Содержательная часть'] = cut_edges.group()
    else:
        dct['Содержательная часть'] = None
    return dct

def inspect_corpus(file, iop_obj, process_func=False):
    reader = csv.DictReader(file, delimiter=';')
    for row in reader:
        if process_func:
            row = process_func(row)
        iop_obj.append(row)



