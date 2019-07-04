import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from pathlib import Path
import calendar
from datetime import date

from atctds_search_civil import debugger as dbg
from .patterns import BuildingInterface

class DateBox(ttk.Frame, BuildingInterface):
    def __init__(self, parent, **kwargs):
        ttk.Frame.__init__(self, parent, **kwargs)
        BuildingInterface.__init__(self)
        self.months = [
            'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
            'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
        ]
        self.months_for_label = [
            'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
            'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'
            ]
        self.label_head = None #label at the widget's top row
        self.label_Y_hint = None
        self.label_M_hint = None
        self.label_D_hint = None
        self.cmb_Year = None
        self.cmb_Month = None
        self.cmb_Day = None
        self.btn_clean_all = None
        self.label_inf_Day = None
        self.label_inf_Month = None
        self.label_inf_Year = None
        #tkinter variables:
        self.l_Day_var = tk.StringVar()
        self.l_Month_var = tk.StringVar()
        self.l_Year_var = tk.StringVar()
        #internal instance data:
        self.flags_date = {flag:False for flag in ('M', 'Y')}
    
    @dbg.method_speaker('Loading external data to DateBox class instance (years)')
    def load_external_data(self, list_of_years):
        self.cmb_Year['values'] = list_of_years
    
    def extract_internal_data(self):
        year = int(self.cmb_Year.get())
        month = self.cmb_Month.current() + 1
        day = int(self.cmb_Day.get())
        return date(year, month, day)

    def count_days_in_month(self):
        self.cmb_Day['state'] = 'readonly'
        year = int(self.cmb_Year.get())
        month = self.cmb_Month.current() + 1
        days_in_month = calendar.monthrange(year, month)[1]
        self.cmb_Day['values'] = [
            str(i) for i in range(1, days_in_month+1, 1)
        ]

    def process_year(self, event):
        self.l_Year_var.set(self.cmb_Year.get())
        self.flags_date['Y'] = True
        if self.flags_date['Y'] and self.flags_date['M']:
            self.count_days_in_month()

    def process_month(self, event):
        ind = self.cmb_Month.current()
        self.l_Month_var.set(self.months_for_label[ind])
        self.flags_date['M'] = True
        if self.flags_date['Y'] and self.flags_date['M']:
            self.count_days_in_month()
    
    @dbg.method_speaker('Cleaning ComboBox widgets!')
    def cmd_clean_all(self):
        self.flags_date = {key:False for key in self.flags_date}
        cmbs = (
            self.cmb_Day,
            self.cmb_Month,
            self.cmb_Year
        )
        l_vars = (
            self.l_Day_var,
            self.l_Month_var,
            self.l_Year_var
        )
        for cmb, l_var in zip (cmbs, l_vars):
            cmb.selection_clear()
            cmb.set('')
            l_var.set('')
        self.cmb_Day['state'] = 'disabled'

    def build_widgets(self):
        #header and hint widgets:
        self.label_head = ttk.Label(
            self,
            text='Выберите дату',
            width=13,
            anchor='center'
        )
        self.label_Y_hint = ttk.Label(
            self,
            text='Г',
            width=2,
            anchor='center'
        )
        self.label_M_hint = ttk.Label(
            self,
            text='М',
            width=2,
            anchor='center'
        )
        self.label_D_hint = ttk.Label(
            self,
            text='Д',
            width=2,
            anchor='center'
        )
        #Combobox widgets:
        self.cmb_Year = ttk.Combobox(
            self,
            textvariable=self.l_Year_var,
            width=15,
            state='disabled'
        )
        self.cmb_Year.bind('<<ComboboxSelected>>', self.process_year)

        self.cmb_Month = ttk.Combobox(
            self,
            values=self.months,
            width=15,
            state='disabled'
        )
        self.cmb_Month.bind('<<ComboboxSelected>>', self.process_month)

        self.cmb_Day = ttk.Combobox(
            self,
            textvariable=self.l_Day_var,
            width=15,
            state='disabled'
        )
        #last row widgets:
        self.btn_clean_all = ttk.Button(
            self,
            text='Х',
            command=self.cmd_clean_all,
            width=2
        )
        self.label_inf_Day = ttk.Label(
            self,
            textvariable=self.l_Day_var,
            anchor='e',
            width=3,
            relief='sunken'
        )
        self.label_inf_Month = ttk.Label(
            self,
            textvariable=self.l_Month_var,
            anchor='center',
            width=11,
            relief='sunken'
        )
        self.label_inf_Year = ttk.Label(
            self,
            textvariable=self.l_Year_var,
            anchor='w',
            width=4,
            relief='sunken'
        )
    
    def grid_inner_widgets(self):
        self.label_head.grid(column=0, row=0, columnspan=4, sticky='we')
        labels_hints = (
            self.label_Y_hint,
            self.label_M_hint,
            self.label_D_hint
        )
        for row_id, label in enumerate(labels_hints, start=1):
            label.grid(column=0, row=row_id, sticky='we')
        self.cmb_Year.grid(column=1, row=1, columnspan=3, sticky='we')
        self.cmb_Month.grid(column=1, row=2, columnspan=3, sticky='we')
        self.cmb_Day.grid(column=1, row=3, columnspan=3, sticky='we')
        self.btn_clean_all.grid(column=0, row=4, sticky='we')
        self.label_inf_Day.grid(column=1, row=4, sticky='e')
        self.label_inf_Month.grid(column=2, row=4, sticky='we')
        self.label_inf_Year.grid(column=3, row=4, sticky='w')
        

###############################################################################
############################### testing: ######################################
###############################################################################

class DateBoxTest(DateBox):
    def __init__(self, parent, **kwargs):
        DateBox.__init__(self, parent=parent, **kwargs)
    
    @dbg.method_speaker('Clearing ComboBox widgets!')
    def clear_all(self):
        self.cmd_clean_all()
    
    @dbg.method_speaker('Print selected date:')
    def extract_internal_data(self):
        year = int(self.cmb_Year.get()) if self.cmb_Year.get() else 1900
        month = self.cmb_Month.current() + 1 if self.cmb_Month.get() else 1
        day = int(self.cmb_Day.get()) if self.cmb_Day.get() else 1
        print('\t', date(year, month, day))

    def start_widget_solo(self):
        self.build_widgets()
        self.cmb_Year['values'] = ('2017', '2018', '2019')
        for cmb in self.cmb_Month, self.cmb_Year:
            cmb['state'] = 'readonly'
        self.label_head.bind('<Double-3>', lambda x: self.clear_all())
        self.label_head.bind(
            '<Double-1>',
            lambda x: self.extract_internal_data()
        )
        self.grid_inner_widgets()
        self.grid(column=0, row=0, sticky='nswe')
        self.mainloop()