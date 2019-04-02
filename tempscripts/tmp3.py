#Building simple IR-system with bollean search and forword index of each
#document

#some multiprocessing stuff
#https://stackoverflow.com/questions/12297892/tkinter-launching-process-via-multiprocessing-creates-not-wanted-new-window
#https://stackoverflow.com/questions/23947281/python-multiprocessing-redirect-stdout-of-a-child-process-to-a-tkinter-text?rq=1


import tempfile
import time
import multiprocessing as mpc
import threading as thrd
import tkinter as tk
from tkinter import ttk

from tempscripts import iotext as iot, textproctool as tpt
from debugger import timer_with_func_name
from guidialogs import ffp, fdp

@timer_with_func_name
def create_inverted_index(corpus_iterator, stpw, tknz, **tknz_kwargs):
    '''
    Unefficient function for creating inverted index table
    corpus_iterator - iterable with strings each of wich represrents document
    tknz - iot.Tokenizer class instance or iot.Tokenizer descendante 
           class instance
    stpw - iterable with stopwords
    tknz_kwargs - keyword arguments for tknz object which are
                  delim, word_len, lem_map
    '''
    iid = {}
    tknz = tknz(corpus_iterator, stpw)
    for ind, tokens_doc in enumerate(tknz):
        if ind % 10000 == 0:
            print(ind)
        tokens_set = set(tokens_doc)
        for token in tokens_set:
            iid.setdefault(token, []).append(ind)
    return iid

class BooleanSearcher():
    '''
    Class implementes boolean serach by constracting inverted indices table
    and also forward indices tables for each document
    '''
    def __init__(self):
        self.forward_index_store = tpt.IOPickler(tempfile.TemporaryFile())
        self.inverted_index = None

    @timer_with_func_name
    def create_inverted_index(self, corpus_iterator, stpw, tknz, **tknz_kwargs):
        '''
        Unefficient function for creating inverted index table
        corpus_iterator - iterable with strings each of wich represrents document
        tknz - iot.Tokenizer class instance or iot.Tokenizer descendante 
            class instance
        stpw - iterable with stopwords
        tknz_kwargs - keyword arguments for tknz object which are
                    delim, word_len, lem_map
        '''
        time1 = time.time()
        iid = {}
        corpus_iterator.find_docs(r'-{66}')
        tknz = tknz(corpus_iterator, stpw)
        for ind, tokened_doc in enumerate(tknz):
            if ind % 10000 == 0:
                print(ind)
            #self.create_forward_index(tokened_doc)
            tokens_set = set(tokened_doc)
            for token in tokens_set:
                iid.setdefault(token, []).append(ind)
        time2 = time.time()
        self.inverted_index = iid
        print('TIME: {: >7.3f} s, {: >5.3f} min'.format(time2-time1, (time2-time1)/60))
    
    def create_forward_index(self, tokened_doc):
        holder = {}
        for ind, token in enumerate(tokened_doc):
            holder.setdefault(token, set()).add(ind)
        self.forward_index_store.append(holder)
    
    def conj_search(self, *words):
        for ind1, word in enumerate(words):
            try:
                primary_set = set(self.inverted_index[word])
            except KeyError:
                print('Word \'{}\' is not in the coprus!'.format(word))
                continue
            break       
        for ind2, word in enumerate(words[ind1:], start=ind1):
            try:
                new_set = self.inverted_index[word]
            except KeyError:
                print('There is no \'{} {}\' in the corpus!'.format(ind2, word))
                continue
            primary_set &= new_set
            if primary_set:
                final_set = primary_set
            else:
                break
        return final_set

def reader(queue_data, queue_len, p1, p2, lock):
    corpus_iterator = iot.MyReaderPre(open(p1, mode='r'))
    corpus_iterator.find_docs(r'-{66}')
    stpw = tpt.rwtools.load_pickle(p2)
    tknz = iot.Tokenizer(corpus_iterator, stpw)
    tknz.process_documents()
    for ind, doc in enumerate(tknz):
        queue_data.put((ind, doc))
    while queue_len:
        queue_data.put((None, None))
        queue_len-=1
    with lock:
        print('READER ENDED!')

def worker(queue_data, queue_iid_part, pid, lock):
    while True:
        ind, doc = queue_data.get()
        if doc == None:
            print('WORKER {: >1d} ENDED!'.format(pid))
            queue_iid_part.put((None, None))
            break
        else:
            if ind % 10000 == 0:
                with lock:
                    print('WORKER {: >1d}: doc # {: >5d}'.format(pid, ind))
            tokens_set = set(doc)
            queue_iid_part.put((ind, tokens_set))

def absorber(queue_iid_part, queue_len, lock):
    common_dct = {}
    semathore = []
    while True:
        ind, iid_part = queue_iid_part.get()
        if iid_part == None:
            semathore.append(None)
            if len(semathore) == queue_len:
                print('ABSORBER ENDED! Total tokens: {: >8d}'.format(
                    len(common_dct))
                )
                break
        else:
            if ind % 10000 == 0:
                with lock:
                    print('ABSORBER: doc # {: >5d}'.format(ind))
            for token in iid_part:
                common_dct.setdefault(token, []).append(ind)

def start(queue_len=3):
    time1 = time.time()
    print('MAIN START!')
    lock = mpc.Lock()

    p1 = ffp()
    p2 = ffp()
    print('Corpus file\n{}'.format(p1))
    print('STPW file\n{}'.format(p2))

    queue_data = mpc.Queue(maxsize=queue_len)
    queue_iid_part = mpc.Queue(maxsize=1)
    
    pr_reader = mpc.Process(
        target=reader, args=(queue_data, queue_len, p1, p2, lock)
    )
    pr_reader.start()

    pr_workers = [
        mpc.Process(target=worker, args=(queue_data, queue_iid_part, i, lock))
        for i in range(queue_len)
    ]
    for pr in pr_workers:
        pr.start()

    pr_absorber = mpc.Process(
        target=absorber, args=(queue_iid_part, queue_len, lock)
    )
    pr_absorber.start()

    pr_reader.join()
    for pr in pr_workers:
        pr.join()
    pr_absorber.join()
    
    print('MAIN ENDED!')
    time2 = time.time()
    print('TIME: {: >7.3f} s, {: >5.3f} min'.format(time2-time1, (time2-time1)/60))

def wrap():
    pr_start = mpc.Process(target=start)
    pr_start.start()
    pr_start.join()

def wrap2():
    w_start = thrd.Thread(target=wrap)
    w_start.start()

def create_widget():
    root = tk.Tk()
    btn = tk.Button(root, command=wrap2, text='Begin processing!')
    btn.pack()
    root.mainloop()

if __name__ == '__main__':
    print('Console mode')
    create_widget()