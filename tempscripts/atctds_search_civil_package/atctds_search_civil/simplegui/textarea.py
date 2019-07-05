import tkinter as tk
from tkinter import ttk

from atctds_search_civil import debugger as dbg
from .patterns import CommonInterface

class TextArea(ttk.Frame, CommonInterface):
    def __init__(self, parent, **kwargs):
        ttk.Frame.__init__(self, parent, **kwargs)
        CommonInterface.__init__(self, parent)
        self.label_head = None # Heading label
        self.txt = None # tk.Text
        self.scrl = None # ttk.Scrollbar
    
    def build_widgets(self):
        self.label_head = ttk.Label(
            self,
            text='Окно информации',
            anchor='center'
        )
        self.txt = tk.Text(
            self,
            state='disabled',
            width=70,
            height=20
        )
        self.scrl = ttk.Scrollbar(
            self,
            orient='vertical',
            command=self.txt.yview
        )
        self.txt['yscrollcommand'] = self.scrl
    
    def grid_inner_widgets(self):
        self.label_head.grid(column=0, row=0, sticky='we')
        self.txt.grid(column=0, row=1, sticky='nwse')
        self.scrl.grid(column=1, row=1, sticky='nws')