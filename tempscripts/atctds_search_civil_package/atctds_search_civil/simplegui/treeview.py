import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from pathlib import Path

from atctds_search_civil import debugger as dbg
from .patterns import CommonInterface


class TreeView(ttk.Frame, CommonInterface):
    def __init__(self, parent, **kwargs):
        ttk.Frame.__init__(self, parent, **kwargs)
        CommonInterface.__init__(self, parent)
        self.info = None
        self.tv = None
        self.btn_1 = None
        self.sort_flag_0 = False
        self.sort_flag_1 = False
        self.counter = tk.IntVar()
    
    def sort(self, region):
        items = []
        for i in self.tv.get_children():
            cnl = self.tv.item(i)['text']
            code = self.tv.item(i)['values'][0]
            items.append((cnl, code))
        self.tv.delete(*self.tv.get_children())
        if region == 'head':
            items = sorted(items, key=lambda x: x[0], reverse=self.sort_flag_0)
        elif region == 'col':
            items = sorted(items, key=lambda x: x[1], reverse=self.sort_flag_0)
        self.sort_flag_0 = not self.sort_flag_0
        for pair in items:
            key, val = pair
            self.tv.insert(
                '',
                'end',
                text=key,
                values=(val,)
            )

    def build_widgets(self):
        self.btn_1 = ttk.Button(
            self,
            text='Подготовить выводы',
            command= lambda: print('Command not specified!'),
            state='disabled'
        )

        self.label_inf = ttk.Label(
            self,
            textvariable=self.counter,
            width=4,
            anchor='e',
            relief='sunken'
        )

        self.tv = ttk.Treeview(self, columns=('ЭСС', ))
        self.tv.heading('#0', text='Кирпич', command= lambda:self.sort('head'))
        self.tv.column('#0', width=100, stretch=True)
        self.tv.heading('ЭСС', text='ЭСС', command=lambda:self.sort('col'))
        self.tv.column('ЭСС', width=65, stretch=True)
        self.tv.bind(
            '<Double-1>',
            lambda x: print(self.tv.item(self.tv.identify('item', x.x, x.y)))
        )
        self.scroll = ttk.Scrollbar(
                    self,
                    orient='vertical',
                    command=self.tv.yview
                )
        self.tv.configure(yscrollcommand=self.scroll.set)
        self.widget_dict = {
            'btn_1': self.btn_1,
            'tv': self.tv
        }
    
    def grid_inner_widgets(self):
        self.tv.grid(column=0, row=0, columnspan=2, sticky='we')
        self.btn_1.grid(column=0, row=1, sticky='we')
        self.label_inf.grid(column=1, row=1, sticky='we')
        self.scroll.grid(column=2, row=0, sticky='nes')