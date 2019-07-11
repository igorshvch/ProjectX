import tkinter as tk
from tkinter import ttk

from atctds_search_civil import debugger as dbg
from .patterns import CommonInterface

class ListView(ttk.Frame, CommonInterface):
    def __init__(self, parent, **kwargs):
        ttk.Frame.__init__(self, parent, **kwargs)
        CommonInterface.__init__(self, parent)
        self.label_scrl = None #label
        self.lstb = None #tk.Listbox
        self.scrl = None #ttk.Scrollbar
        self.btn_clean_all = None
        self.label_count1 = None #label with description of the following widget
        self.label_count2 = None #label to count quantity of loaded conclusions
        self.lstb_var = tk.StringVar()
        self.l_count_var = tk.StringVar()
    
    @dbg.method_speaker('Cleaning ListView widgets!')
    def cmd_clean_all(self):
        self.lstb_var.set('')
        self.l_count_var.set('')

    def build_widgets(self):
        self.lb_scrl = ttk.Label(
            self,
            text='Список выводов (кирпичей)',
            anchor='center',
            width=30,
            relief='flat'
        )
        self.lstb = tk.Listbox(
            self,
            listvariable=self.lstb_var,
            height=10,
            width=50,
            selectmode='extended'
        )
        self.scrl = ttk.Scrollbar(
            self,
            orient='vertical',
            command=self.lstb.yview
        )
        self.lstb['yscrollcommand'] = self.scrl.set
        self.btn_clean_all = ttk.Button(
            self,
            text='X',
            command=self.cmd_clean_all,
            width=2,
            state='disabled'
        )
        self.label_count1 = ttk.Label(
            self,
            text='Всего выводов:',
            anchor='e',
            relief='flat'
        )
        self.label_count2 = ttk.Label(
            self,
            textvariable=self.l_count_var,
            anchor='e',
            width=4,
            relief='sunken'
        )
        self.widget_dict = {
            'lstb': self.lstb,
            'btn_clean_all': self.btn_clean_all
        }
    
    def grid_inner_widgets(self):
        self.lb_scrl.grid(column=0, row=0, columnspan=3, sticky='we')
        self.lstb.grid(column=0, row=1, columnspan=3, sticky='we')
        self.scrl.grid(column=3, row=1, sticky='nws')
        self.btn_clean_all.grid(column=0, row=2, sticky='w')
        self.label_count1.grid(column=1, row=2, sticky='e')
        self.label_count2.grid(column=2, row=2, sticky='e')

###############################################################################
############################### testing: ######################################
###############################################################################

from atctds_search_civil.testtools import rd, gts

class ListViewTest(ListView):
    def __init__(self, parent, **kwargs):
        ListView.__init__(self, parent, **kwargs)  

    @dbg.method_speaker('Inserting randomly generated data!')
    def insert_data(self):
        data = gts(rd.randint(3,20))
        count = str(len(data))
        self.lstb_var.set(data)
        self.l_count_var.set(count)
    
    @dbg.method_speaker('Deleting data!')
    def erase_data(self):
        self.lstb_var.set('')
        self.l_count_var.set('')
    
    def start_widget(self):
        self.build_widgets()
        self.btn_clean_all['state'] = 'normal'
        self.lstb.bind('<Double-1>', lambda x: self.insert_data())
        self.lstb.bind('<Double-3>', lambda x: self.erase_data())
        self.grid_inner_widgets()