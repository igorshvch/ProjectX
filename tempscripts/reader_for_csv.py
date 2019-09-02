import sys
import re
import csv
import pathlib as pthl
from datetime import date

import iopickler as iop
from textproc import rwtools


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
    #'find_act_content': lambda x: re.search(
    #    r'(?<=\nустановил:\n).*(?=\nПредседательствующий|\nПредседательствующий судья)',
    #    x,
    #    flags=re.DOTALL
    #).group(),
    'string_to_date': lambda x: string_to_date(x),
    'separate_act_ids': lambda x: set(x.split(',')),
    'court': lambda x: x.split('_')[0],
    'sinopsis': lambda x: re.split(r',(?=[\w\n-])', x, maxsplit=1)
}

def custom_processor_for_ConsPlus_data(dct):
    req_name = dct['Название документа']
    #if req_name[:6] == 'Постан':
    name, sinopsis = data_trans_funcs['sinopsis'](req_name)
    dct['Название документа'] = name
    dct['Описание'] = sinopsis
    #else:
    #    dct['Описание'] = rew_name
    text = dct['Текст документа']
    comas_to_newlines = data_trans_funcs['comas_to_newlines'](text)
    dct['Текст документа'] = comas_to_newlines
    #try:
    #    content = data_trans_funcs['find_act_content'](comas_to_newlines)
    #except:
    #    content = None
    #dct['Содержание'] = content
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

class MyReaderCSV():
    def __init__(self, p_file=None):
        if p_file:
            path = p_file.parent
            name = p_file.stem
            file_dates = rwtools.create_new_binary(name+'_dates', path)
            file_docreq = rwtools.create_new_binary(name+'_docreqs', path)
            self.doc_store = iop.IOPickler(file=p_file)
            self.date_holder = iop.IOPickler(file=file_dates)
            self.docreq_holer = iop.IOPickler(file=file_docreq)
        else:
            self.doc_store = iop.IOPickler()
            self.date_holder = iop.IOPickler()
            self.docreq_holer = iop.IOPickler()
            print('Using tempfiles')
        self.dates_loading = dict()
        self.dates_issue = dict()
        self.docreqs = dict()
        self.names = dict()
    
    def inspect_corpus(self,
                       file,
                       process_func=custom_processor_for_ConsPlus_data):
        reader = csv.DictReader(file, delimiter=';')
        for ind, row in enumerate(reader):
            if process_func:
                row = process_func(row)
            self.doc_store.append(row)
            for date in row['Когда получен']:
                self.dates_loading.setdefault(date, []).append(ind)
            for date in row['Дата']:
                self.dates_issue.setdefault(date, []).append(ind)
            for req in row['Номер']:
                self.docreqs.setdefault(req, []).append(ind)
            self.names.setdefault(row['Название документа'], []).append(ind)


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

