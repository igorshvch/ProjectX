#https://stackoverflow.com/questions/7310511/how-to-create-downloading-progress-bar-in-ttk
#https://stackoverflow.com/questions/24769798/tkinter-progressbar-linked-to-function
#https://stackoverflow.com/questions/24764575/using-the-same-progressbar-in-tkinter-for-several-computation

import tkinter as tk
from tkinter import ttk

#from tempscripts import iotext as it

#fp = r'C:\Users\EA-ShevchenkoIS\AppData\Local\Continuum\anaconda3\ProjectX\2018-0725-0803_174_info.txt'
#mr = it.MyReader(open(fp, mode='r'))

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
        self.maxbytes = 50000
        self.progress["maximum"] = self.maxbytes
        self.read_bytes()

    def read_bytes(self):
        '''simulate reading 500 bytes; update progress bar'''
        self.bytes += 500
        self.progress["value"] = self.bytes
        if self.bytes < self.maxbytes:
            # read more bytes after 100 ms
            self.after(100, self.read_bytes)

app = SampleApp()
app.mainloop()