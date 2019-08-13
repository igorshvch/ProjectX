import tkinter as tk
from tkinter import ttk
from threading import (
    Thread, 
    Lock,
    Event,
    active_count,
    get_ident,
    current_thread
)
from queue import Queue
from time import sleep

LOCK = Lock()
EVENT = Event()

q = Queue(maxsize=1)

def start_print():
    if not EVENT.is_set():
        EVENT.set()
    with LOCK:
        thrd = Thread(target=printer, args=())
        thrd.start()

def printer():
    idn = get_ident()
    speaker = 'Thread {: >6d}, daemon={}:'.format(
        idn,
        current_thread().isDaemon()
    )
    while EVENT.is_set():
        #try:
        #    val = q.get(block=False)
        #    if val == 'stop!':
        #        break
        #except:
        #    pass
        print(speaker, '"Jaw" was never my film and I don\'t like "Star Wars"!')
        sleep(1)

def stop_print():
    #if q.full():
    #    with LOCK:
    #        print('Queue is temporary unavailable!')
    #else:
    #    q.put('stop!')
    #    with LOCK:
    #        print('Put "stop!" command in queue!')
    with LOCK:
        print('Active threads:', active_count())
        print('Stop printing!')
    EVENT.clear()
    sleep(1)
    with LOCK:
        print('Active threads:', active_count(), '(main thread)')

def info_print():
    with LOCK:
        print('Active threads:', active_count())

def start_button(root):
    btn = ttk.Button(
        root,
        text='Start printing!',
        command=start_print
    )
    btn2 = ttk.Button(
        root,
        text='Stop!',
        command=stop_print
    )
    btn3 = ttk.Button(
        root,
        text='Active threads',
        command=info_print
    )
    btn.pack()
    btn2.pack()
    btn3.pack()
    root.mainloop()


if __name__ == '__main__':
    start_button(tk.Tk())
