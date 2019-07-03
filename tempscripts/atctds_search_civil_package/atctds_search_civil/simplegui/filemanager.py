import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from pathlib import Path

from atctds_search_civil import debugger as dbg


class FileManager(ttk.Frame):
    def __init__(self, parent=tk.Tk(), **kwargs):
        ttk.Frame.__init__(self, parent, **kwargs)
        self.l_CD_var = tk.StringVar() #Court Desicions
        self.l_CNL_var = tk.StringVar() #Conclusions
        self.l_Save_var = tk.StringVar()
        self.btn_clean_all = None
        self.btn_Load = None
        self.btn_CD = None #Court Desicions
        self.btn_CNL = None #Conclusions
        self.btn_Save = None
        self.label_Load = None
        self.label_CD = None #Court Desicions
        self.label_CNL = None #Conclusions
        self.label_Save = None
    
    def extract_internal_data(self):
        tk_string_vars = {
            'CD': self.l_CD_var,
            'CNL': self.l_CNL_var,
            'Save': self.l_Save_var
        }
        res = {key:val for key,val in tk_string_vars.items()}
        return res

    @dbg.method_speaker('Cleaning all widgets!')
    def cmd_clean_all(self):
        btns = (
            self.btn_Load,
            self.btn_CD,
            self.btn_CNL,
            self.btn_Save
        )
        tk_string_vars = (
            self.l_CD_var,
            self.l_CNL_var,
            self.l_Save_var
        )
        for btn in btns:
            btn['state'] = 'normal'
        for tk_string_var in tk_string_vars:
            tk_string_var.set('')
    
    @dbg.method_speaker('Chose path to court desicions!')
    def cmd_CD(self): #Court Desicions
        self.btn_Load['state'] = 'disabled'
        folder_path = fd.askdirectory(
            initialdir=Path().home().joinpath('Робот')
        )
        if len(folder_path) >= 100:
            folder_path = '...'+folder_path[-93:]
        self.l_CD_var.set(folder_path)
        self.btn_CD['state'] = 'disabled'

    @dbg.method_speaker('Loading previously saved corpus data!')
    def cmd_Load(self):
        self.btn_CD['state'] = 'disabled'
        folder_path = fd.askdirectory(
            initialdir=Path().home().joinpath('Робот', 'Предыдущие сеансы')
        )
        if len(folder_path) >= 100:
            folder_path = '...'+folder_path[-93:]
        self.l_CD_var.set(folder_path)
        self.btn_Load['state'] = 'disabled'
    
    @dbg.method_speaker('Chose path to file with conclusions!')
    def cmd_CNL(self): #Conclusions
        self.btn_CNL['state'] = 'disabled'
        file_path = fd.askopenfilename(
            initialdir=Path().home().joinpath('Робот')
        )
        if len(file_path) >= 100:
            file_path = '...'+file_path[-93:]
        self.l_CNL_var.set(file_path)
    
    @dbg.method_speaker('Chose path to results save folder!')
    def cmd_Save(self):
        self.btn_Save['state'] = 'disabled'
        folder_path = fd.askdirectory(
            initialdir=Path().home().joinpath('Робот')
        )
        if len(folder_path) >= 100:
            folder_path = '...'+folder_path[-93:]
        self.l_Save_var.set(folder_path)
    
    @dbg.method_speaker('Cleaning string var!')
    def cmd_clean(self, widget_var):
        options = {
            'CD': (self.l_CD_var, (self.btn_CD, self.btn_Load)),
            'CNL': (self.l_CNL_var, (self.btn_CNL,)),
            'Save': (self.l_Save_var, (self.btn_Save,))
        }
        options[widget_var][0].set('')
        for btn in options[widget_var][1]:
            btn['state'] = 'normal'

    def build_widgets(self):
        self.btn_clean_all = ttk.Button(
            self,
            text='Очистить\n      все',
            command=self.cmd_clean_all,
            width=9
        )
        self.btn_CD = ttk.Button( #Court Desicions
            self,
            text='Новые суд.акты',
            command=self.cmd_CD,
            width=17
        )
        self.btn_Load = ttk.Button(
            self,
            text='Загрузить обработанные',
            command=self.cmd_Load,
            width=23
        )
        self.btn_CNL = ttk.Button( #Conclusions
            self,
            text='Путь к кирпичам',
            command=self.cmd_CNL,
            width=42
        )
        self.btn_Save = ttk.Button(
            self,
            text='Путь сохранения результатов',
            command=self.cmd_Save,
            width=42
        )
        self.label_CD = ttk.Label( #Court Desicions
            self,
            textvariable=self.l_CD_var,
            anchor='w',
            width=100,
            relief='sunken'
        )
        self.label_CNL = ttk.Label( #Conclusions
            self,
            textvariable=self.l_CNL_var,
            anchor='w',
            width=100,
            relief='sunken'
        )
        self.label_Save = ttk.Label(
            self,
            textvariable=self.l_Save_var,
            anchor='w',
            width=100,
            relief='sunken'
        )
        self.btn_clean_CD = ttk.Button(
            self,
            text='X',
            command=lambda: self.cmd_clean('CD'),
            width=2
        )
        self.btn_clean_CNL = ttk.Button(
            self,
            text='X',
            command=lambda: self.cmd_clean('CNL'),
            width=2
        )
        self.btn_clean_Save = ttk.Button(
            self,
            text='X',
            command=lambda: self.cmd_clean('Save'),
            width=2
        )
    
    def grid_inner_widgets(self):
        self.btn_clean_all.grid(column=0, row=0, rowspan=3, sticky='ns')
        self.btn_CD.grid(column=1, row=0, sticky='we')
        self.btn_Load.grid(column=2, row=0, sticky='w')
        self.btn_CNL.grid(column=1, row=1, columnspan=2, sticky='w')
        self.btn_Save.grid(column=1, row=2, columnspan=2, sticky='w')

        labels = (self.label_CD, self.label_CNL, self.label_Save)
        for row_id, label in enumerate(labels):
            label.grid(column=3, row=row_id, sticky='we')

        clean_btns = (
            self.btn_clean_CD, self.btn_clean_CNL, self.btn_clean_Save
        )
        for row_id, btn_clean in enumerate(clean_btns):
            btn_clean.grid(column=4, row=row_id, sticky='w')
    
    def start_widget(self):
        self.build_widgets()
        self.grid_inner_widgets()
        self.mainloop()
    
    def start_widget_solo(self):
        self.build_widgets()
        self.grid_inner_widgets()
        self.grid(column=0, row=0, sticky='wnes')
        self.mainloop()