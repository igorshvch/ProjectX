import multiprocessing as mpc
from multiprocessing import Queue
from queue import (
    Empty as queueErrorEmpty,
    Full as queueErrorFull
)
from time import sleep
import random
import tkinter as tk
from tkinter import ttk
import sys

global_lock = mpc.Lock()

def producer(lock, queue_in):
    with lock:
        print(
            'Producer', mpc.current_process().name
        )
    alph = [chr(i) for i in range(1040, 1072, 1)]
    while True:
        word = ''.join(random.choices(alph, k=5)).capitalize()
        queue_in.put(word)


def consumer(lock, ind, queue_in, queue_out):
    with lock:
        print(
            'IND: {}'.format(ind), mpc.current_process().name,
            'Consumer Process starts!'
        )
    sleep(3)
    while True:
        #sleep(random.randint(1,2))
        if queue_in.empty():
            continue
            #with lock:
            #    print(
            #        'IND: {}'.format(ind), mpc.current_process().name,
            #        'Queue empty!'
            #    )
            #break
        item = queue_in.get()
        string = ' '.join(
            ('IND: {}'.format(ind), mpc.current_process().name,
            'get item!', 'Item: {}'.format(item), '\n')
        )
        #with lock:
        #    print(string)
        queue_out.put(string)

def launcher(diapason, global_lock=global_lock):
    lock = global_lock
    queue_in = Queue(maxsize=diapason)
    queue_out = Queue(maxsize=1000)
    prod = mpc.Process(target=producer, args=(lock, queue_in))
    prod.start()
    cons = {
        i:mpc.Process(target=consumer, args=(lock, i, queue_in, queue_out))
        for i in range(diapason)
    }
    for i in cons:
        cons[i].start()
    #prod.join()
    #for i in cons:
    #    i.join()
    return queue_out, cons, prod

def create_widget(queue, queue_control, global_lock=global_lock):
    def inner_f(queue_control, lock):
        with lock:
            print('GUI', 'Terminate random proc!')
        queue_control.put('terminate')
    lock = global_lock
    root = tk.Tk()
    text = tk.Text(root)
    scroll = ttk.Scrollbar(
        root,
        orient='vertical',
        command=text.yview
    )
    button = ttk.Button(
        root,
        text='Term proc',
        command=lambda: inner_f(queue_control, global_lock)
    )
    text.configure(yscrollcommand=scroll.set)
    text.grid(column=0, row=0, sticky='nwse')
    scroll.grid(column=1, row=0, sticky='nes')
    button.grid(column=0, row=1, sticky='nwse')
    with lock:
        print(
            'GUI', mpc.current_process().name, 'start mainloop'
        )
    #tk.mainloop()
    while True:
        if queue.empty():
            sleep(0.5)
            text.update()
            continue
        item = queue.get()
        text.insert('end', item)
        #text.see('end')
        #sleep(0.5)
        text.update()

def gui_in_dep_proc(queue, queue_control, global_lock=global_lock):
    gui = mpc.Process(
        target=create_widget, args=(queue, queue_control, global_lock)
    )    
    gui.start()
    return gui


if __name__ == '__main__':
    print('START!')
    queue_out, cons_procs, prod = launcher(int(sys.argv[1]))
    queue_control = Queue(maxsize=3)
    sleep(3)
    gui = gui_in_dep_proc(queue_out, queue_control, global_lock=global_lock)
    while True:
        try:
            item = queue_control.get()
            with global_lock:
                print('MAIN', 'item:', item)
            if item:
                prs = cons_procs.popitem()[1]
                prs_name = prs.name
                prs.terminate()
                with global_lock:
                    print('MAIN', prs_name, 'Process terminated')
                sleep(0.5)
                if not prs.is_alive():
                    prs.join()
                    with global_lock:
                        print('MAIN', prs_name, 'Process joined')
        except:
            with global_lock:
                print('MAIN', 'Control queue is empty!')
            gui.terminate()
            prod.terminate()
            with global_lock:
                print('MAIN', 'GUI Process and Producer Process terminated')
            sleep(0.5)
            if (not gui.is_alive()) and (not prod.is_alive()):
                gui.join()
                prod.join()
                with global_lock:
                    print('MAIN', 'GUI Process and Producer Process joined')
                break

