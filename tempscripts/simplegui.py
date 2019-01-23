#Treeview issue:
#https://stackoverflow.com/questions/49715456/forcing-a-tkinter-ttk-treeview-widget-to-resize-after-shrinking-its-column-width

import tkinter as tk
from tkinter import ttk

from guidialogs import ffp, fdp

class TreeviewBuilder():
    def __init__(self, root=None):
        self.root = root if root else tk.Tk()
        self.info = None
        self.tv = None
        self.btn1 = None
        self.data = None
        self.sort_flag_0 = False
        self.sort_flag_1 = False
        self.sort_flag_2 = False
    
    def btn1_cmd(self):
        #print(self.tv.selection())
        if not self.tv.selection():
            return None
        for i in self.tv.selection():
            print(self.tv.item(i))

    def define(self, event):
        region = self.tv.identify('region', event.x, event.y)
        if region == 'heading':
            col = self.tv.identify('column', event.x, event.y)
            return col
    
    def sort0(self):
        self.tv.delete(*self.tv.get_children())
        self.data = sorted(self.data, key=lambda x: x[0], reverse=self.sort_flag_0)
        self.sort_flag_0 = not self.sort_flag_0
        for triple in self.data:
            key, val1, val2 = triple
            self.tv.insert(
                '',
                'end',
                text=key,
                values=(val1, val2)
            )
    
    def sort1(self):
        self.tv.delete(*self.tv.get_children())
        self.data = sorted(self.data, key=lambda x: x[1], reverse=self.sort_flag_1)
        self.sort_flag_1 = not self.sort_flag_1
        for triple in self.data:
            key, val1, val2 = triple
            self.tv.insert(
                '',
                'end',
                text=key,
                values=(val1, val2)
            )
    
    def sort2(self):
        self.tv.delete(*self.tv.get_children())
        self.data = sorted(self.data, key=lambda x: x[2], reverse=self.sort_flag_2)
        self.sort_flag_2 = not self.sort_flag_2
        for triple in self.data:
            key, val1, val2 = triple
            self.tv.insert(
                '',
                'end',
                text=key,
                values=(val1, val2)
            )

    def build_Treeview(self, head, cols, data):
        self.data = data
        self.btn1 = ttk.Button(self.root, text='Print selected', command=self.btn1_cmd)
        self.tv = ttk.Treeview(self.root, columns=cols)
        self.tv.heading('#0', text=head, command=self.sort0)
        self.tv.column('#0', width=100, stretch=True)
        for i, cmd in zip(cols, (self.sort1, self.sort2)):
            self.tv.heading(i, text=str(i), command=cmd)
            self.tv.column(i, width=40, stretch=True)
        for triple in data:
            key, val1, val2 = triple
            self.tv.insert(
                '',
                'end',
                text=key,
                values=(val1, val2)
            )
        #tv.bind('<Double-3>', lambda x: inner_f(x))
        #tv.bind('<Double-1>', lambda x: print(tv.item(tv.identify('item', x.x, x.y))))
        #tv.bind('<Double-2>', lambda x: print(tv.get_children('')))
        #tv.bind('<<TreeviewSelect>>', lambda x: print('Select!'))
        self.tv.bind(
            '<Double-1>',
            lambda x: print(self.tv.item(self.tv.identify('item', x.x, x.y)))
        )
    
    def start_widget(self):
        self.btn1.pack(fill='x', expand='yes')
        self.tv.pack(fill='x', expand='yes')
        self.root.mainloop()


class Filesloader():
    def __init__(self, root=None):
        self.root = root if root else tk.Tk()
        self.st_var = tk.StringVar()
        self.btn1 = None
        self.btn2 = None
        self.inf_label = None
    
    def btn1_cmd(self):
        self.path = ffp()
        self.st_var.set(self.path)
        self.btn1.configure(state='disabled')
        #self.inf_label.update()
    
    def btn2_cmd(self):
        for btn in self.btn1, self.btn2:
            btn.configure(state='normal')

    def build_Loader(self):
        self.btn1 = ttk.Button(
            self.root,
            text='Подгрузить данные о файле',
            command=self.btn1_cmd
        )            
        self.btn2 = ttk.Button(
            self.root,
            text='Enable state!',
            command=self.btn2_cmd
        )
        self.inf_label = tk.Text(
            self.root,
            textvariable=self.st_var,
            background='pink',
            width=40
        )
    
    def start_widget(self):
        self.btn1.pack(fill='x', expand='yes')
        self.inf_label.pack(fill='x', expand='yes')
        self.btn2.pack(fill='x', expand='yes')
        self.root.mainloop()





