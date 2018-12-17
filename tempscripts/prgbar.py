#https://stackoverflow.com/questions/7310511/how-to-create-downloading-progress-bar-in-ttk
#https://stackoverflow.com/questions/24769798/tkinter-progressbar-linked-to-function
#https://stackoverflow.com/questions/24764575/using-the-same-progressbar-in-tkinter-for-several-computation

import tkinter as tk
from tkinter import ttk

from tempscripts import iotext as it

fp = r'C:\Users\EA-ShevchenkoIS\AppData\Local\Continuum\anaconda3\ProjectX\2018-0725-0803_174_info.txt'
mr = it.MyReader_iter(open(fp, mode='r'))

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

app = SampleApp()
app.mainloop()