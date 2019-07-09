import tkinter as tk
from tkinter import ttk

from atctds_search_civil import debugger as dbg
from .patterns import CommonInterface

class ControlButtons(ttk.Frame, CommonInterface):
    def __init__(self, parent, **kwargs):
        ttk.Frame.__init__(self, parent, **kwargs)
        CommonInterface.__init__(self, parent)
        self.btn_Start = None
        self.btn_clean_all = None
    
    @dbg.method_speaker()
    def cmd_clean_all(self):
        return None
    
    @dbg.method_speaker('Cleaning all programm data for new iteration')
    def cmd_Start(self):
        return None
    
    def build_widgets(self):
        self.btn_Start = ttk.Button(
            self,
            text='\nЗапустить анализ\n',
            command=self.cmd_Start
        )
        self.btn_clean_all = ttk.Button(
            self,
            text='\nНовый сеанс\n',
            command=self.cmd_clean_all
        )
    
    def grid_inner_widgets(self):
        self.btn_Start.grid(column=0, row=0, sticky='we')
        self.btn_clean_all.grid(column=0, row=1, sticky='we')