import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from pathlib import Path

from atctds_search_civil import debugger as dbg
from .patterns import CommonInterface


class ProgBar(ttk.Frame, CommonInterface):
    def __init__(self, parent, **kwargs):
        ttk.Frame.__init__(self, parent, **kwargs)
        CommonInterface.__init__(self, parent)
        self.prog_bar = None
    
    def build_widgets(self):
        self.prog_bar = ttk.Progressbar(
            self,
            orient='horizontal',
            length=900,
            mode='indeterminate'
        )
    
    def grid_inner_widgets(self):
        self.prog_bar.grid(column=0, row=0, sticky='we')