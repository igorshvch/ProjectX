from csv import (
    writer as csv_writer,
    QUOTE_MINIMAL as csv_QUOTE_MINIMAL
)
from pathlib import Path
from time import time

__version__ = '0.2.8'

###Content=====================================================================
GLOB_ENC = 'cp1251'

def collect_exist_files(top_dir, suffix=''):
    holder = []
    def inner_func_with_suf(top_dir, suffix, holder):
        p = Path(top_dir)
        store = [path_obj for path_obj in p.iterdir()]
        for path_obj in store:
            if path_obj.is_dir():
                inner_func_with_suf(path_obj, suffix, holder)
            elif path_obj.suffix == suffix:
                holder.append(path_obj)
    def inner_func_without_suf(top_dir, holder):
        p = Path(top_dir)
        store = [path_obj for path_obj in p.iterdir()]
        for path_obj in store:
            if path_obj.is_dir():
                inner_func_without_suf(path_obj, holder)
            elif path_obj.is_file():
                holder.append(path_obj)
    if suffix:
        inner_func_with_suf(top_dir, suffix, holder)
    else:
        inner_func_without_suf(top_dir, holder)
    return sorted(holder)

def collect_exist_dirs(top_dir):
    holder = []
    def inner_func(top_dir, holder):
        p = Path(top_dir)
        store = [path_obj for path_obj in p.iterdir() if path_obj.is_dir()]
        for path_obj in store:
            holder.append(path_obj)
            inner_func(path_obj, holder)
    inner_func(top_dir, holder)
    return sorted(holder)

def collect_exist_files_and_dirs(top_dir, suffix=''):
    holder = []
    def inner_func_with_suf(top_dir, suffix, holder):
        p = Path(top_dir)
        store = [path_obj for path_obj in p.iterdir()]
        for path_obj in store:
            if path_obj.is_dir():
                holder.append(path_obj)
                inner_func_with_suf(path_obj, suffix, holder)
            elif path_obj.suffix == suffix:
                holder.append(path_obj)
    def inner_func_without_suf(top_dir, holder):
        p = Path(top_dir)
        store = [path_obj for path_obj in p.iterdir()]
        for path_obj in store:
            if path_obj.is_dir():
                holder.append(path_obj)
                inner_func_without_suf(path_obj, holder)
            elif path_obj.is_file():
                holder.append(path_obj)
    if suffix:
        inner_func_with_suf(top_dir, suffix, holder)
    else:
        inner_func_without_suf(top_dir, holder)
    return sorted(holder)

def read_text(path, encoding=GLOB_ENC):
    with open(str(path), mode='r', encoding=encoding) as fle:
        text = fle.read()
    return text

def write_text(text, path, encoding=GLOB_ENC):
    if path[-4:] != '.txt':
        path += '.txt'
    with open(path, mode='w', encoding=encoding) as fle:
        fle.write(text)

def write_iterable_to_csv(full_path,
                          iter_txt_holder,
                          header=None,
                          zero_string=None,
                          encoding=GLOB_ENC):
    with open(full_path, mode='w', newline='', encoding=encoding) as fle:
        writer = csv_writer(
            fle,
            delimiter='|',
            quotechar='#',
            quoting=csv_QUOTE_MINIMAL
        )
        if zero_string:
            zero_string = (
                [zero_string] + ['na' for i in range(len(header)-1)]
            )
            assert len(zero_string) == len(header)
            writer.writerow(zero_string)
        if header:
            writer.writerow(header)
        for row in iter_txt_holder:
            writer.writerow(row)

def save_pickle(py_obj, path):
    import pickle
    with open(path, mode='wb') as file_name:
        pickle.dump(py_obj,
                    file_name,
                    protocol=pickle.HIGHEST_PROTOCOL)
        
def load_pickle(path, mode='rb'):
    import pickle
    with open(path, mode=mode) as fle:
        data = pickle.load(fle)
    return data            

def save_object(py_obj, name, save_folder):
    save_folder = Path(save_folder)
    path = save_folder.joinpath(name)
    save_pickle(py_obj, str(path))

def create_new_binary(file_name, folder):
    return open(Path(folder).joinpath(file_name), mode='a+b')


###Testing=====================================================================
if __name__ == '__main__':
    import sys
    try:
        sys.argv[1]
        if sys.argv[1] == '-v':
            print('Module name: {}'.format(sys.argv[0]))
            print('Version info:', __version__)
        elif sys.argv[1] == '-t':
            print('Testing mode!')
            print('Not implemented!')
        else:
            print('Not implemented!')
    except IndexError:
        print('Mode var wasn\'t passed!')
