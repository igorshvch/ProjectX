import multiprocessing as mpc
from queue import Empty, Full
from time import sleep
import random
import tkinter as tk
from tkinter import ttk
import sys
import os
import time

#moment stamp:
#time.strftime('%Y-%m-%d %H:%M:%S')

global_lock = mpc.Lock()

class Main():
    def __init__(self, num):
        self.num = num
        self.root = tk.Tk()
        self.q_cons_c = mpc.Queue(maxsize=1)
        self.q_prod_c = mpc.Queue(maxsize=1)
        self.q_cons_f = mpc.Queue(maxsize=1000)
        #self.q_prod_f = mpc.Queue(maxsize=1000)
        self.q_pipe = mpc.Queue(maxsize=num)
        self.conss = {}
        self.prods = {}

    def create_widgets(self):
        root = self.root
        self.text = tk.Text(root)
        self.scroll = ttk.Scrollbar(
            root,
            orient='vertical',
            command=self.text.yview
        )
        self.text.configure(yscrollcommand=self.scroll.set)
        self.btn_1 = ttk.Button(
            root,
            text='Start Consumer',
            command=self.start_cons
        )
        self.btn_2 = ttk.Button(
            root,
            text='Start Producer',
            command=self.start_prod
        )
        self.btn_3 = ttk.Button(
            root,
            text='Stop Consumer',
            command=self.stop_cons
        )
        self.btn_4 = ttk.Button(
            root,
            text='Stop Producer',
            command=self.stop_prod
        )
        self.btn_5 = ttk.Button(
            root,
            text='Stop all',
            command=self.stop_all
        )

        self.text.grid(column=0, row=0, sticky='nwse')
        self.scroll.grid(column=1, row=0, sticky='nes')
        self.btn_1.grid(column=0, row=1, sticky='nw')
        self.btn_2.grid(column=0, row=2, sticky='nw')
        self.btn_3.grid(column=0, row=3, sticky='nw')
        self.btn_4.grid(column=0, row=4, sticky='nw')
        self.btn_5.grid(column=0, row=5, sticky='nw')
        self.root.mainloop()
    
    def insert_info(self, *msg):
        msg = ' '.join(msg)
        msg = (
            time.strftime('%Y/%m/%d %H:%M:%S')
            +' >>>' + ' ' + msg + '\n'+'-'*69
        )
        self.text.insert('end', msg+'\n')
        self.text.see('end')
    
    def __name(self, x: int, t='c'):
        if t == 'c':
            return 'Consumer{:0>5d}'.format(x)
        elif t == 'p':
            return 'Producer{:0>5d}'.format(x)

    def start_cons(self):
        name = self.__name(len(self.conss)+1, t='c')
        cons = Consumer(name, self.q_pipe, self.q_cons_c, self.q_cons_f, global_lock)
        self.q_cons_c.put('START')
        self.conss[name] = mpc.Process(target=cons.start, args=())
        self.conss[name].start()
        self.insert_info('Consumer "{}" started!'.format(name))
    
    def start_prod(self):
        name = self.__name(len(self.prods)+1, t='p')
        prod = Producer(name, self.q_pipe, self.q_prod_c, global_lock)
        self.q_prod_c.put('START')
        self.prods[name] = mpc.Process(target=prod.start, args=())
        self.prods[name].start()
        self.insert_info('Producer "{}" started!'.format(name))
    
    def stop_cons(self):
        try:
            self.q_cons_c.put('STOP', timeout=0.1)
        except Full:
            self.insert_info('Consumers\' control queue is full')
    
    def stop_prod(self):
        try:
            self.q_prod_c.put('STOP', timeout=0.1)
        except Full:
            self.insert_info('Produsers\' control queue is full')
    
    def stop_all(self):
        if not self.conss or not self.prods:
            self.insert_info('Create consumer or producer!')
            return None
        for key in self.conss:
            self.conss[key].terminate()
            if not self.conss[key].is_alive():
                self.conss[key].join()
        for key in self.prods:
            self.prods[key].terminate()
            if not self.prods[key].is_alive():
                self.prods[key].join()


class Producer():
    def __init__(self, ind, queue_pipe, queue_control, lock):
        self.ind = ind
        self.q_pipe = queue_pipe
        self.q_ctrl = queue_control
        self.lock = lock
    
    def start(self):
        alph = [chr(i) for i in range(1040, 1072, 1)]
        flag = False
        while True:
            if not flag:
                try:
                    command = self.q_ctrl.get(timeout=0.1)
                    if command == 'START':
                        with self.lock:
                            print(self.ind, '1st', 'Start execution!')
                        flag = True
                except:
                    pass
            else:
                try:
                    command = self.q_ctrl.get(timeout=0.1)
                    if command == 'STOP':
                        with self.lock:
                            print(self.ind, '1st', 'Stop execution!')
                        flag = False
                        continue
                except:
                    pass
                finally:
                    word = ''.join(random.choices(alph, k=5)).capitalize()
                    self.q_pipe.put(word)

class Consumer():
    def __init__(self, ind, queue_pipe, queue_control, queue_feedback, lock):
        self.ind = ind
        self.q_pipe = queue_pipe
        self.q_ctrl = queue_control
        self.q_fdbk = queue_feedback
        self.lock = lock
    
    def start(self):
        flag = False
        while True:
            if not flag:
                try:
                    command = self.q_ctrl.get(timeout=0.1)
                    if command == 'START':
                        with self.lock:
                            print(self.ind, '1st', 'Start execution!')
                        flag = True
                except:
                    pass
            else:
                try:
                    command = self.q_ctrl.get(timeout=0.1)
                    if command == 'STOP':
                        with self.lock:
                            print(self.ind, '1st', 'Stop execution!')
                        flag = False
                        continue
                except:
                    pass
                finally:
                    word = self.q_pipe.get()
                    self.q_fdbk.put(('OUTPUT', self.ind, word))

if __name__ == '__main__':
    gui = Main(int(sys.argv[1]))
    gui.create_widgets()