#https://stackoverflow.com/questions/7310511/how-to-create-downloading-progress-bar-in-ttk
#https://stackoverflow.com/questions/24769798/tkinter-progressbar-linked-to-function
#https://stackoverflow.com/questions/24764575/using-the-same-progressbar-in-tkinter-for-several-computation

import tkinter as tk
from tkinter import ttk
from time import sleep

from tempscripts import iotext as it

#fp = r'C:\Users\EA-ShevchenkoIS\AppData\Local\Continuum\anaconda3\ProjectX\2018-0725-0803_174_info.txt'
#mr = it.MyReader_iter(open(fp, mode='r'))

class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.button = ttk.Button(text="start", command=self.start)
        self.button.pack()
        self.progress = ttk.Progressbar(self, orient="horizontal",
                                        length=200, mode="determinate")
        self.progress.pack()

        self.bytes = 0
        self.maxbytes = 0

    def start(self):
        self.progress["value"] = 0
        self.hold_obj = mr
        self.maxbytes = self.hold_obj.file_size
        self.progress["maximum"] = self.maxbytes
        self.process = self.hold_obj.find_docs(r'Когда получен\n', r'Текст документа\n', r'-{66}')
        self.read_bytes()

    def read_bytes(self):
        '''simulate reading 500 bytes; update progress bar'''
        while self.bytes < self.maxbytes:
            next(self.process)
            self.bytes += self.hold_obj.state
            self.progress["value"] = self.bytes
            self.update()

        #next(self.process)
        #self.bytes += self.hold_obj.state
        #self.progress["value"] = self.bytes
        #if self.bytes < self.maxbytes:
        #    # read more bytes after 100 ms
        #    self.after(100, self.read_bytes)

#app = SampleApp()
#app.mainloop()

class SampleApp2(tk.Tk):

    def __init__(self, *args, funcbox=None, func=None, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.button = ttk.Button(text="start", command=self.start)
        self.button.pack()
        self.progress = ttk.Progressbar(self, orient="horizontal",
                                        length=200, mode="determinate")
        self.progress.pack()
        self.hold_obj = funcbox
        self.func = func.__name__


    def start(self):
        self.gen = getattr(self.hold_obj, self.func)()
        self.button["state"] = 'disabled'
        self.process()
        self.button["state"] = 'normal'

    def process(self):
        '''simulate function processing'''
        pos = 0
        stop = 1
        while pos < stop:
            sleep(0.1)
            pos, res= next(self.gen)
            print(self.hold_obj.text, pos, res)
            self.progress["value"] = pos*100
            self.update()
        sleep(0.1)
        self.progress["value"] = 0
        self.update()

class FuncBox():
    def __init__(self):
        self.text = None
        self.step = None
    def f1(self):
        position = 0
        stop = 1000
        step = 100
        self.text = 'This is f1 function, step {:d}'.format(step)
        while position < stop:
            position += step
            yield position/stop, position
    def f2(self):
        position = 0
        stop = 1000
        step = 25
        self.text = 'This is f2 function, step {:d}'.format(step)
        while position < stop:
            position += step
            yield position/stop, position
    def f3(self):
        position = 0
        stop = 2794
        step = 25
        self.text = 'This is f3 function, step {:d}'.format(step)
        while position < stop:
            position += step
            yield position/stop, position

