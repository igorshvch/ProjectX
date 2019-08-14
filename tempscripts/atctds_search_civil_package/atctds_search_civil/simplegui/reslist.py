import tkinter as tk
from tkinter import ttk

from atctds_search_civil import debugger as dbg
from atctds_search_civil.simplegui.patterns import (
    CommonInterface, CustomTextWidgetRu
)


class ResList(ttk.Frame, CommonInterface):
    def __init__(self, parent, icon_path=None, **kwargs):
        ttk.Frame.__init__(self, parent, **kwargs)
        CommonInterface.__init__(self, parent)
        self.label_res_lstb = None
        self.res_lstb = None
        self.scrl_y = None
        self.scrl_x = None
        self.btn_clean_all = None
        self.label_count1 = None
        self.label_count2 = None
        self.res_lstb_var = tk.StringVar()
        self.res_l_count_var = tk.StringVar()
        self.icon_path = icon_path
    
    @dbg.method_speaker('Cleaning ResList widgets!')
    def cmd_clean_all(self):
        self.res_lstb_var.set('')
        self.res_l_count_var.set('')
        self.btn_clean_all['state'] = 'disabled'

    def build_widgets(self):
        self.label_res_lstb = ttk.Label(
            self,
            text='Найденные акты',
            anchor='center'
        )
        self.res_lstb = tk.Listbox(
            self,
            listvariable=self.res_lstb_var,
            height=15,
            width=50,
            selectmode='browse'
        )

        self.scrl_y = ttk.Scrollbar(
            self,
            orient='vertical',
            command=self.res_lstb.yview
        )
        self.res_lstb['yscrollcommand'] = self.scrl_y.set
        self.scrl_x = ttk.Scrollbar(
            self,
            orient='horizontal',
            command=self.res_lstb.xview
        )
        self.res_lstb['xscrollcommand'] = self.scrl_x.set

        self.btn_clean_all = ttk.Button(
            self,
            text='X',
            command=self.cmd_clean_all,
            width=2,
            state='disabled'
        )
        self.label_count1 = ttk.Label(
            self,
            text='Найдено актов: ',
            anchor='e',
        )
        self.label_count2 = ttk.Label(
            self,
            textvariable=self.res_l_count_var,
            anchor='e',
            width=2,
            relief='sunken'
        )
    
    def grid_inner_widgets(self):
        self.label_res_lstb.grid(column=0, row=0, columnspan=3, sticky='we')
        self.res_lstb.grid(column=0, row=1, columnspan=3, sticky='we')
        self.scrl_y.grid(column=3, row=1, sticky='nws')
        self.scrl_x.grid(column=0, row=2, columnspan=3, sticky='enw')
        self.btn_clean_all.grid(column=0, row=3, sticky='w')
        self.label_count1.grid(column=1, row=3, sticky='e')
        self.label_count2.grid(column=2, row=3, sticky='e')
        self.columnconfigure(0, weight=1)


###############################################################################
############################### testing: ######################################
###############################################################################

if __name__ == '__main__':
    root = tk.Tk()
    rlt = ResList(root)
    rlt.start_widget_solo()