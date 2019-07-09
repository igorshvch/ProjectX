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
        self.btn_clean_all = None
    
    @dbg.method_speaker('Cleaning TextArea widgets!')
    def cmd_clean_all(self):
        self.txt['state'] = 'normal'
        self.txt.delete('1.0', 'end')
        self.txt['state'] = 'disabled'
    
    @dbg.method_speaker('Printing text to InfoWindow!')
    def print_in(self, text):
        self.txt['state'] = 'normal'
        self.txt.insert('end', text+'\n')
        self.txt.see('end')
        self.txt['state'] = 'disabled'
    
    @dbg.method_speaker('Loading external data to TextArea class instance!')
    def load_external_data(self, log_message):
        self.print_in(log_message)
    
    def build_widgets(self):
        self.label_head = ttk.Label(
            self,
            text='Окно информации',
            anchor='center'
        )
        self.txt = tk.Text(
            self,
            state='disabled',
            width=72,
            height=18
        )
        self.scrl = ttk.Scrollbar(
            self,
            orient='vertical',
            command=self.txt.yview
        )
        self.txt['yscrollcommand'] = self.scrl
        self.btn_clean_all = ttk.Button(
            self,
            text='X',
            command=self.cmd_clean_all,
            width=2
        )
    
    def grid_inner_widgets(self):
        self.label_head.grid(column=0, row=0, sticky='we')
        self.txt.grid(column=0, row=1, sticky='nwse')
        self.scrl.grid(column=1, row=1, sticky='nws')
        self.btn_clean_all.grid(column=0, row=2, sticky='w')

###############################################################################
############################### testing: ######################################
###############################################################################

from .testtools import rd, gts

class TextAreaTest(TextArea):
    def __init__(self, parent, **kwargs):
        TextArea.__init__(self, parent, **kwargs)
    
    def insert_data(self):
        data = gts(rd.randint(3,20))
        while data:
            text = data.pop()
            self.load_external_data(text)

    def start_widget(self):
        self.build_widgets()
        self.txt.bind('<Double-2>', lambda x: self.insert_data())
        self.grid_inner_widgets()
    
