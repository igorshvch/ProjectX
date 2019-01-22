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

def f2(dct):
    dct = list(dct.items())
    def button_cmd():
        print(tv.selection())
    def inner_f(x):
        region = tv.identify('region', x.x, x.y)
        if region == 'heading':
            col = tv.identify('column', x.x, x.y)
            print(col)
    def fill_in(column):
        pass        
    cols=['class', 'facts']
    root = tk.Tk()
    btn1 = ttk.Button(root, text='Print selected', command=button_cmd)
    tv = ttk.Treeview(root, columns=cols)
    tv.heading('#0', text='concls')
    tv.column('#0', width=100, stretch=True)
    for i in cols:
        tv.heading(i, text=str(i))
        tv.column(i, width=40, stretch=True)
    for pair in dct:
        for key, val in pair:
           tv.insert('', 'end', text=val, values=key)
    tv.bind('<Double-3>', lambda x: inner_f(x))
    #tv.bind('<Double-1>', lambda x: print(tv.item(tv.identify('item', x.x, x.y))))
    #tv.bind('<Double-2>', lambda x: print(tv.get_children('')))
    #tv.bind('<<TreeviewSelect>>', lambda x: print('Select!'))
    btn1.pack(fill='x', expand='yes')
    tv.pack(fill='x', expand='yes')
    root.mainloop()