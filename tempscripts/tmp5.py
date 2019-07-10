import tkinter as tk
from tkinter import ttk
from threading import Thread, Lock, active_count
from queue import Queue
from time import sleep

lock = Lock()

q = Queue(maxsize=1)

def start_print():
    with lock:
        thrd = Thread(target=printer, args=())
        thrd.start()

def printer():
    while True:
        try:
            val = q.get(block=False)
            if val == 'stop!':
                break
        except:
            pass
        print('"Jaw" was never my film and I don\'t like "Star Wars"!')
        sleep(1)

def stop_print():
    if q.full():
        with lock:
            print('Queue is temporary unavailable!')
    else:
        q.put('stop!')
        with lock:
            print('Put "stop!" command in queue!')

def info_print():
    with lock:
        print(active_count())

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
