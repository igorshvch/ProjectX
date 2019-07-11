import tkinter as tk
from tkinter import ttk
import multiprocessing as mpc
from os import getpid
from queue import Queue
from time import sleep


def start_print(q):
    proc = mpc.Process(target=printer, args=(q,))
    proc.start()

def printer(q):
    pn = getpid()
    speaker = 'Process # '+str(pn)
    while True:
        try:
            val = q.get(block=False)
            if val == 'stop':
                print('\t', speaker, 'GET TEMINATION CODE!')
                break
            else:
                print('\t', speaker, 'Couldn\'t get the termination code!', val)
        except:
            print('\t', speaker, 'Catch an exception!')
        print('\t', speaker, '"Jaw" was never my film and I don\'t like "Star Wars"!')
        sleep(1)

def stop_print(q, btn):
    if q.full():
        print('Queue is full!')
    else:
        q.put('stop', block=False)
        print('Put "stop" command in queue!')
    sleep(2)
    if len(mpc.active_children()) == 1:
        btn['state'] = 'normal'
    else:
        btn['state'] = 'disabled'

def info_print():
    processes = [str(i) for i in mpc.active_children()]
    if processes:
        print(', '.join(processes))
    else:
        print('No active subprocesses were found!')

def shutdown_manager(m, btn1, btn2):
    m.shutdown()
    for btn in btn1, btn2:
        btn['state'] = 'disabled'

def start_buttons(root):
    m = mpc.Manager()
    q = m.Queue(maxsize=1)
    btn = ttk.Button(
        root,
        text='Start printing!',
        command=lambda: start_print(q)
    )
    btn2 = ttk.Button(
        root,
        text='Stop!',
        command=lambda: stop_print(q, btn4)
    )
    btn3 = ttk.Button(
        root,
        text='Active processes',
        command=lambda: info_print()
    )
    btn4 = ttk.Button(
        root,
        text='Shutdown!',
        command=lambda: shutdown_manager(m, btn, btn2),
        state='disabled'
    )

    btn.pack(fill='both', expand='yes')
    btn2.pack(fill='both', expand='yes')
    btn3.pack(fill='both', expand='yes')
    btn4.pack(fill='both', expand='yes')

    root.mainloop()


if __name__ == '__main__':
    start_buttons(tk.Tk())