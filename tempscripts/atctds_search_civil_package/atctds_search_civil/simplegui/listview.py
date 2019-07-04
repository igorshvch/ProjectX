import tkinter as tk
from tkinter import ttk

from atctds_search_civil import debugger as dbg
from .patterns import BuildingInterface

class ListView(ttk.Frame, BuildingInterface):
    def __init__(self, parent, **kwargs):
        ttk.Frame.__init__(self, parent, **kwargs)
        BuildingInterface.__init__(self)
        self.label_scrl = None #label
        self.lstb = None #tk.Listbox
        self.scrl = None #ttk.Scrollbar
        self.label_count1 = None #label with description of the following widget
        self.label_count2 = None #label to count quantity of loaded conclusions
        self.lstb_var = tk.StringVar()
        self.l_count_var = tk.StringVar()

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
        self.label_count1 = ttk.Label(
            self,
            text='Всего выводов:',
            anchor='w',
            width=14,
            relief='flat'
        )
        self.label_count2 = ttk.Label(
            self,
            textvariable=self.l_count_var,
            anchor='e',
            width=4,
            relief='sunken'
        )
    
    def grid_inner_widgets(self):
        self.lb_scrl.grid(column=0, row=0, columnspan=3, sticky='we')
        self.lstb.grid(column=0, row=1, columnspan=2, sticky='we')
        self.scrl.grid(column=2, row=1, sticky='ns')
        self.label_count1.grid(column=0, row=2, sticky='we')
        self.label_count2.grid(column=1, row=2, columnspan=2, sticky='e')

###############################################################################
############################### testing: ######################################
###############################################################################

import random as rd

def generate_tokens_secquence(length=5):
    alph = [chr(i) for i in range(97, 123, 1)]
    holder = []
    while length:
        holder.append(''.join(rd.choices(alph, k=rd.randint(3,7))).capitalize())
        length-=1
    return holder

gts = generate_tokens_secquence


class ListViewTest(ListView):
    def __init__(self, parent, **kwargs):
        ListView.__init__(self, parent, **kwargs)  

    @dbg.method_speaker('Inserting randomly generated data!')
    def _insert_data(self):
        data = gts(rd.randint(3,20))
        count = str(len(data))
        self.lstb_var.set(data)
        self.l_count_var.set(count)
    
    @dbg.method_speaker('Deleting data!')
    def _erase_data(self):
        self.lstb_var.set('')
        self.l_count_var.set('')
    
    def start_widget_solo(self):
        self.build_widgets()
        self.lstb.bind('<Double-1>', lambda x: self._insert_data())
        self.lstb.bind('<Double-3>', lambda x: self._erase_data())
        self.grid_inner_widgets()
        self.grid(column=0, row=0, sticky='nswe')
        self.mainloop()