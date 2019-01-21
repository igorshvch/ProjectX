#Treeview issue:
#https://stackoverflow.com/questions/49715456/forcing-a-tkinter-ttk-treeview-widget-to-resize-after-shrinking-its-column-width

import tkinter as tk
from tkinter import ttk

class MyGui(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.mainframe = ttk.Frame(self)
        self.mainframe.grid()

def f(items):
    cols=['one', 'two', 'three', 'four']
    root = tk.Tk()
    tv = ttk.Treeview(root, columns=cols)
    tv2 = ttk.Treeview(root, columns=cols)
    for i in cols:
        tv.heading(i, text=str(i))
        tv.column(i, width=40, stretch=False)
    for i in range(len(items)):
        tv.insert('', 'end', values=(items[i],))
    tv2.heading('#0', text='HSBGCN')
    tv2.column('#0', width=60, stretch=False)
    for i in cols:
        tv2.heading(i, text=str(i))
        tv2.column(i, width=40, stretch=False)
    for i in range(len(items)):
        tv2.insert('', 'end', text=items[i], values=('',))
    tv.configure(show='headings')
    tv.pack()
    tv2.pack()
    root.mainloop()