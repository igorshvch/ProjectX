import re
import csv
import tempfile
import pathlib as pthl
import pickle as pkl
from datetime import date

from tempscripts import iopickler as iop
from textproc import rwtools
from guidialogs import ffp, fdp


def string_to_date(string):
    ddates = []
    if ',' in string:
        dates = string.split(',')
        for item in dates:
            parts = item.split('.')
            ddate = date(int(parts[2]), int(parts[1]), int(parts[0]))
            ddates.append(ddate)
        return max(ddates)
    else:
        parts = string.split('.')
        ddate = date(int(parts[2]), int(parts[1]), int(parts[0]))
        return ddate

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
    'sinopsis': lambda x: re.split(r',(?=[\w\n-()])', x, maxsplit=1)
}

def custom_processor_for_ConsPlus_data(counter, dct):
    req_name = dct['Название документа']
    r_name = req_name[:6]
    if (
        r_name != 'Постан' and
        r_name != 'Апелля' and
        r_name != 'Опреде' and
        r_name != 'Решени'
    ):
        return counter, None
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
    counter += 1
    return counter, dct

def inspect_corpus(file,
                   iop_obj=None,
                   process_func=custom_processor_for_ConsPlus_data):
    if not iop_obj:
        iop_obj = iop.IOPickler()
    reader = csv.DictReader(file, delimiter=';')
    for row in reader:
        if process_func:
            _, row = process_func(0, row)
            if not row:
                continue
        iop_obj.append(row)
    return iop_obj


class MyReaderCSV_Base():
    def __init__(self):
        self.doc_store = []
        self.dates_loading = dict()
        self.dates_issue = dict()
        self.docreqs = dict()
        self.names = dict()
        self.dates_info = dict()
    
    def __len__(self):
        return len(self.doc_store)

    def __getitem__(self, index):
        return self.doc_store[index]
    
    def __iter__(self):
        for doc in self.doc_store:
            yield doc


class MyReaderCSV(MyReaderCSV_Base):
    def __init__(self, source=None, p_file=None):
        MyReaderCSV_Base.__init__(self)
        if p_file:
            self.doc_store = iop.IOPickler(file=p_file)
        else:
            self.doc_store = iop.IOPickler(file=tempfile.TemporaryFile())
        ##########
        if source:
            self.inspect_corpus(source)
    
    def inspect_corpus(self,
                       source,
                       index_start=0,
                       process_func=custom_processor_for_ConsPlus_data):
        counter = index_start
        reader = csv.DictReader(source, delimiter=';')
        for row in reader:
            if process_func:
                counter, row = process_func(counter, row)
                if not row:
                    continue 
            self.doc_store.append(row)
            date_l = row['Когда получен']
            self.dates_loading.setdefault(date_l, []).append(counter)
            date_i = row['Дата']
            self.dates_issue.setdefault(date_i, []).append(counter)
            for req in row['Номер']:
                self.docreqs.setdefault(req, []).append(counter)
            self.names.setdefault(row['Название документа'], []).append(counter)
        self.dates_info['loading_max'] = max(self.dates_loading.keys())
        self.dates_info['loading_min'] = min(self.dates_loading.keys())
        self.dates_info['issue_max'] = max(self.dates_issue.keys())
        self.dates_info['issue_min'] = min(self.dates_issue.keys())
        source.close()
        self.source = source.name
    
    def find_by_date(self, date_obj, mode='loading'):
        options = {
            'loading': self.dates_loading,
            'issue': self.dates_issue
        }
        if date_obj in options[mode]:
            for ind in options[mode][date_obj]:
                yield self[ind]
        else:
            raise KeyError('"{}" date not found'.format(date_obj))
    
    def find_by_name(self, name, mode='full_match'):
        if mode == 'full_match':
            if name in self.names:
                for ind in self.names[name]:
                    yield self[ind]
            else:
                raise KeyError('"{}" name not found'.format(name))
        if mode == 'contains':
            holder_keys = []
            for key in self.names.keys():
                if name in key:
                    holder_keys.append(key)
            if holder_keys:
                for key in holder_keys:
                    for ind in self.names[key]:
                        yield self[ind]
            else:
                raise KeyError('"{}" name not found'.format(name))

 
class MyReaderCSV_testing(MyReaderCSV):
    def print_stats(self):
        import random as rd
        if not self.dates_loading:
            print('Need to inspect corpus first!')
            return None
        length = len(self)
        doc_ind = rd.randint(0, length)
        doc_info = self[doc_ind]
        print()
        print('-'*101)
        print('Corpus information:')
        print('\tCorpus source:')
        print('\t\t{}'.format(self.source))
        print('\tCorpus underlay:')
        print('\t\t{}'.format(self.doc_store.file_name))
        print('\tCorpus length:')
        print('\t\t{} documents in total'.format(length))
        print('-'*101)
        print('\tRandom document information:')
        print('\t\tDocument ID: {}'.format(doc_ind))
        print('-'*101)
        print('{: >30s}|{: <50s}|{: >19s}'.format('Key', 'Data', 'Type'))
        print('-'*101)
        for key in doc_info.keys():
            data = doc_info[key]
            t = type(data)
            data = str(data).replace('\n', '##')
            if len(data)>45:
                data = data[:45]+'...'
            print(
                '{: >30s}|{: <50s}|{: >19s}'.format(
                    str(key)[:30], data, str(t)
                )
            )
        print('-'*101)
        print()


class CommonReader_Base():
    def __init__(self):
        self.readers = dict()
        self.dates_info = dict()
        self.index = []
    
    def __len__(self):
        if not self.readers:
            print('None readers found!')
            return 0
        counter = 0
        for key in self.readers:
            counter += len(self.readers[key])
        return counter
    
    def __iter__(self):
        if not self.readers:
            print('None readers found!')
            return None
        for key in sorted(self.readers.keys()):
            yield from self.readers[key]
    
    def __getitem__(self, index):
        key, index = self.index[index]
        return self.readers[key][index]



class CommonReader(CommonReader_Base):
    def __init__(self, folder):
        CommonReader_Base.__init__(self)
        self.folder = folder
    
    def __find_dates_range(self, mode='loading'):
        dates_max = []
        dates_min = []
        for key in self.readers:
            dates_max.append(self.readers[key].dates_info[mode+'_max'])
            dates_min.append(self.readers[key].dates_info[mode+'_min'])
        self.dates_info[mode+'_max'] = max(dates_max)
        self.dates_info[mode+'_min'] = min(dates_min)
    
    def __create_total_index(self):
        for key in sorted(self.readers.keys()):
            for i in range(len(self.readers[key])):
                self.index.append((key, i))
    
    def create_readers(self):
        fp = rwtools.collect_exist_files(self.folder, suffix='.csv')
        for path in sorted(fp):
            source = open(path, mode='r', newline='')
            name = path.stem
            if name in self.readers:
                ind_start = len(self.readers[name])
                self.readers[name].inspect_corpus(
                    source=source,
                    index_start=ind_start
                )
            else:
                self.readers[name] = MyReaderCSV(source=source)
        self.__create_total_index()
        self.__find_dates_range(mode='loading')
        self.__find_dates_range(mode='issue')
    
    def find_by_date(self, date_obj, mode='loading'):
        for key in sorted(self.readers.keys()):
            yield from self.readers[key].find_by_date(date_obj, mode=mode)
    
    def find_by_name(self, name, mode='full_match'):
        for key in sorted(self.readers.keys()):
            yield from self.readers[key].find_by_name(name, mode=mode)


if __name__ == '__main__':
    import sys
    from time import time
    mode = sys.argv[1]
    if mode == '-s':
        time1 = time()
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
            print(
                '{: >30s}|{: <50s}|{: >19s}'.format(
                    str(key)[:30], data, str(t)
                )
            )
        print('-'*101)
        time2 = time()
        time_res = time2-time1
        print('time: {: >7.3f} min ({: >7.3f} sec)'.format(
                time_res/60, time_res
            )
        )
    elif mode == '-p':
        summa = 0
        fp = rwtools.collect_exist_files(fdp(), suffix='.csv')
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
                length = len(iop_obj)
                print('OK;', 'acts in total: {}'.format(length))
                summa += length
        time2 = time()
        time_res = time2-time1
        print('Corpus contains {} acts'.format(summa))
        print('time: {: >7.3f} min ({: >7.3f} sec)'.format(
                time_res/60, time_res
            )
        )
    elif mode == '-c':
        time1 = time()
        with open(ffp(), mode='r', newline='') as f:
            print(f.name)
            mrcsv = MyReaderCSV_testing()
            mrcsv.inspect_corpus(source=f)
            mrcsv.print_stats()
        time2 = time()
        time_res = time2-time1
        print('time: {: >7.3f} min ({: >7.3f} sec)'.format(
                time_res/60, time_res
            )
        )
    elif mode == '-cr':
        time1 = time()
        cr = CommonReader(fdp())
        cr.create_readers()
        time2 = time()
        time_res = time2-time1
        print('Documents in total: {}'.format(len(cr)))
        print('time: {: >7.3f} min ({: >7.3f} sec)'.format(
                time_res/60, time_res
            )
        )
    else:
        print(
            'Mode arg error! Please type correct mode arg:',
            '-s for single mode, -p for pipline mode'
        )

