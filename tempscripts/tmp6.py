import tkinter as tk
from tkinter import ttk
from multiprocessing import Process, Lock, Queue, active_children
from os import getpid
from queue import Queue
from time import sleep


def start_print(q, lock):
    proc = Process(target=printer, args=(q, lock))
    proc.start()

def printer(q, lock):
    pn = getpid()
    speaker = 'Process # '+str(pn)
    while True:
        try:
            val = q.get(block=False)
            if val == 'stop!':
                with lock:
                    print(speaker, 'GET TEMINATION CODE!')
                break
            else:
                with lock:
                    print(speaker, 'Couldn\'t get the termination code!', val)
        except:
            with lock:
                print(speaker, 'Catch an exception!')
        print(speaker, '"Jaw" was never my film and I don\'t like "Star Wars"!')
        sleep(1)
    #while True:
    #    try:
    #        val = q.get(block=False, timeout=5)
    #        with lock:
    #            print(speaker, 'Value from queue:', val)
    #        if val == 'stop!':
    #            with lock:
    #                print(speaker, 'GET TEMINATION CODE!')
    #            break
    #        else:
    #            with lock:
    #                print(speaker, 'Couldn\'t get the termination code!', val)
    #    except:
    #        with lock:
    #            print(speaker, 'Catch an exception!')
    #    print(speaker, '"Jaw" was never my film and I don\'t like "Star Wars"!')
    #    sleep(1)

def stop_print(q, lock):
    if q.full():
        with lock:
            print('Queue is full!')
            print('Queue item:', q.get())
    else:
        q.put('stop!', block=False, timeout=0.2)
        with lock:
            print('Put "stop!" command in queue!')

def info_print(lock):
    with lock:
        print(', '.join(str(i) for i in active_children()))

def start_button(root, q, lock):
    btn = ttk.Button(
        root,
        text='Start printing!',
        command=lambda: start_print(q, lock)
    )
    btn2 = ttk.Button(
        root,
        text='Stop!',
        command=lambda: stop_print(q, lock)
    )
    btn3 = ttk.Button(
        root,
        text='Active processes',
        command=lambda: info_print(lock)
    )
    btn.pack()
    btn2.pack()
    btn3.pack()
    root.mainloop()


if __name__ == '__main__':
    lock = Lock()
    q = Queue(maxsize=1)
    q.put('Nothing!')
    start_button(tk.Tk(), q, lock)