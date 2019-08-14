import tkinter as tk
from tkinter import ttk

from atctds_search_civil import debugger as dbg
from atctds_search_civil.simplegui.patterns import (
    CommonInterface, CustomTextWidgetRu
)

class ResArea(ttk.Frame, CommonInterface):
    def __init__(self, parent, **kwargs):
        ttk.Frame.__init__(self, parent, **kwargs)
        CommonInterface.__init__(self, parent)
        self.notebook = None
        self.tab_00 = None
        self.tab_01 = None
        self.content_00_doc_text = None
        self.content_01_results_list = None
    
    def build_widgets(self):
        self.notebook = ttk.Notebook(self)
        self.tab_00 = CustomTextWidgetRu(
            self.notebook,
            #t_width=90,
            t_height=40
        )
        self.tab_01 = ttk.Frame(self.notebook)
        #self.content_01_results_list = None
        self.notebook.add(
            self.tab_00,
            text='Текст выбранного акта'
        )
        self.notebook.add(
            self.tab_01,
            text='Оценка найденных актов',
            state='disabled'
        )
    
    def grid_inner_widgets(self):
        self.tab_00.start_widget()
        self.notebook.grid(column=0, row=0, sticky='wnes')
        #self.content_01_results_list.grid(column=0, row=0, sticky='nwse')
        #self.tab_00.grid(column=0, row=0, sticky='wnse')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

