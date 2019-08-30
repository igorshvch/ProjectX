import sys
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
        r'(?<=\nустановил:\n).*(?=\nПредседательствующий|\nПредседательствующий судья)',
        x,
        flags=re.DOTALL
    ).group(),
    'string_to_date': lambda x: string_to_date(x),
    'separate_act_ids': lambda x: set(x.split(',')),
    'court': lambda x: x.split('_')[0],
    'sinopsis': lambda x: re.split(r',(?=[\w\n-])', x, maxsplit=1)
}

def custom_processor_for_ConsPlus_data(dct):
    req_name = dct['Название документа']
    if req_name[:6] != 'Постан':
        return None
    name, sinopsis = data_trans_funcs['sinopsis'](req_name)
    dct['Название документа'] = name
    dct['Описание'] = sinopsis
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
    dct['Дата'] = data_trans_funcs['string_to_date'](date_issue)
    req_num = dct['Номер']
    dct['Номер'] = data_trans_funcs['separate_act_ids'](req_num)
    try:
        req_court = dct['Принявший орган']
    except:
        req_court = dct['Судья']
    dct['Принявший орган'] = data_trans_funcs['court'](req_court)
    return dct

def inspect_corpus(file,
                   iop_obj=iop.IOPickler(),
                   process_func=custom_processor_for_ConsPlus_data):
    reader = csv.DictReader(file, delimiter=';')
    for row in reader:
        if process_func:
            row = process_func(row)
            if not row:
                continue
        iop_obj.append(row)
    return iop_obj


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == '-s':
        from guidialogs import ffp
        with open(ffp(), mode='r', newline='') as f:
            print(f.name)
            iop_obj = inspect_corpus(f)
        row = iop_obj[0]
        print('-'*101)
        print('{: >30s}|{: <50s}|{: >19s}'.format('Key', 'Data', 'Type'))
        print('-'*101)
        for key in row.keys():
            data = row[key]
            t = type(data)
            data = str(data).replace('\n', '##')
            if len(data)>45:
                data = data[:45]+'...'
            print('{: >30s}|{: <50s}|{: >19s}'.format(str(key)[:30], data, str(t)))
        print('-'*101)
    elif mode == '-p':
        from guidialogs import fdp
        from textproc import collect_exist_files
        from time import time
        fp = collect_exist_files(fdp(), suffix='.csv')
        time1 = time()
        for ind, path in enumerate(fp):
            with open(path, mode='r', newline='') as f:
                print(ind, 'chek:', path.stem, end=' ')
                iop_obj = inspect_corpus(f)
                row = iop_obj[0]
                for key in row.keys():
                    data = row[key]
                    t = type(data)
                    data = str(data).replace('\n', '##')
                    if len(data)>45:
                        data = data[:45]+'...'
                print('OK')
        time2 = time()
        time_res = time2-time1
        print('time: {: >7.3f} min ({: >7.3f} sec)'.format(
            time_res/60, time_res)
        )

    else:
        print(
            'Mode arg error! Please type correct mode arg:',
            '-s for single mode, -p for pipline mode'
        )

