import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from pathlib import Path

from atctds_search_civil import debugger as dbg
from .patterns import CommonInterface


class FileManager(ttk.Frame, CommonInterface):
    def __init__(self, parent, **kwargs):
        ttk.Frame.__init__(self, parent, **kwargs)
        CommonInterface.__init__(self, parent)
        self.l_CD_var = tk.StringVar() #Court Desicions
        self.l_CNL_var = tk.StringVar() #Conclusions
        self.l_Save_var = tk.StringVar()
        self.label_head = None #Heading label
        self.btn_clean_all = None
        self.btn_Load = None
        self.btn_CD = None #Court Desicions
        self.btn_CNL = None #Conclusions
        self.btn_Save = None
        self.btn_clean_CD = None
        self.btn_clean_CNL = None
        self.btn_clean_Save = None
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

    @dbg.method_speaker('Cleaning FileManager widgets!')
    def cmd_clean_all(self):
        btns_disabling = (
            self.btn_clean_all,
            self.btn_clean_CD,
            self.btn_clean_CNL,
            self.btn_clean_Save
        )
        btns_normalizing = (
            self.btn_Load,
            self.btn_CD,
            self.btn_CNL,
            self.btn_Save,
        )
        tk_string_vars = (
            self.l_CD_var,
            self.l_CNL_var,
            self.l_Save_var
        )
        for btn in btns_normalizing:
            btn['state'] = 'normal'
        for btn in btns_disabling:
            btn['state'] = 'disabled'
        for tk_string_var in tk_string_vars:
            tk_string_var.set('')
    
    @dbg.method_speaker('Chose path to court desicions or to previously saved corpus data!')
    def cmd_CD_or_Load(self, widget_var):
        opritons = {
            'CD': ('Робот',),
            'Load': ('Робот', 'Предыдущие сеансы'),
        }
        folder_path = fd.askdirectory(
            initialdir=Path().home().joinpath(*opritons[widget_var])
        )
        if not folder_path:
            return None
        self.l_CD_var.set(folder_path)
        if len(folder_path) >= 100:
            folder_path = '...'+folder_path[-93:]
        self.btn_CD['state'] = 'disabled'
        self.btn_Load['state'] = 'disabled'
        for btn in self.btn_clean_CD, self.btn_clean_all:
            btn['state'] = 'normal'

#################legacy code starts:    
    @dbg.method_speaker('Chose path to court desicions!')
    def cmd_CD(self): #Court Desicions
        folder_path = fd.askdirectory(
            initialdir=Path().home().joinpath('Робот')
        )
        if not folder_path:
            return None
        self.l_CD_var.set(folder_path)
        if len(folder_path) >= 100:
            folder_path = '...'+folder_path[-93:]
        self.btn_CD['state'] = 'disabled'
        self.btn_Load['state'] = 'disabled'
        for btn in self.btn_clean_CD, self.btn_clean_all:
            btn['state'] = 'normal'

    @dbg.method_speaker('Loading previously saved corpus data!')
    def cmd_Load(self):
        folder_path = fd.askdirectory(
            initialdir=Path().home().joinpath('Робот', 'Предыдущие сеансы')
        )
        if not folder_path:
            return None
        self.l_CD_var.set(folder_path)
        if len(folder_path) >= 100:
            folder_path = '...'+folder_path[-93:]
        self.btn_CD['state'] = 'disabled'
        self.btn_Load['state'] = 'disabled'
        for btn in self.btn_clean_CD, self.btn_clean_all:
            btn['state'] = 'normal'
#################legacy code ends

    @dbg.method_speaker('Chose path to file with conclusions!')
    def cmd_CNL(self): #Conclusions
        file_path = fd.askopenfilename(
            initialdir=Path().home().joinpath('Робот')
        )
        if not file_path:
            return None
        self.l_CNL_var.set(file_path)
        self.btn_CNL['state'] = 'disabled'
        for btn in self.btn_clean_CNL, self.btn_clean_all:
            btn['state'] = 'normal'
    
    @dbg.method_speaker('Chose path to results save folder!')
    def cmd_Save(self):
        folder_path = fd.askdirectory(
            initialdir=Path().home().joinpath('Робот')
        )
        if not folder_path:
            return None
        self.l_Save_var.set(folder_path)
        self.btn_Save['state'] = 'disabled'
        for btn in self.btn_clean_Save, self.btn_clean_all:
            btn['state'] = 'normal'
    
    @dbg.method_speaker('Cleaning string var!')
    def cmd_clean(self, widget_var):
        options = {
            'CD': (
                self.l_CD_var,
                (self.btn_CD, self.btn_Load),
                self.btn_clean_CD,
                (self.l_CNL_var, self.l_Save_var)
            ),
            'CNL': (
                self.l_CNL_var,
                (self.btn_CNL,),
                self.btn_clean_CNL,
                (self.l_CD_var, self.l_Save_var)
            ),
            'Save': (
                self.l_Save_var,
                (self.btn_Save,),
                self.btn_clean_Save,
                (self.l_CD_var, self.l_CNL_var)
            )
        }
        options[widget_var][0].set('')
        for btn in options[widget_var][1]:
            btn['state'] = 'normal'
        options[widget_var][2]['state'] = 'disabled'
        if (
            not options[widget_var][3][0].get()
            and
            not options[widget_var][3][1].get()
        ):
            self.btn_clean_all['state'] = 'disabled'

    def build_widgets(self):
        self.label_head = ttk.Label( #Court Desicions
            self,
            text = 'Выберите пути для загрузки и сохранения файлов:',
            anchor='center'
        )
        self.btn_clean_all = ttk.Button(
            self,
            text='Х',
            command=self.cmd_clean_all,
            width=2,
            state='disabled'
        )
        self.btn_CD = ttk.Button( #Court Desicions
            self,
            text='Новые судебные акты',
            command= lambda: self.cmd_CD_or_Load('CD'),
            width=17
        )
        self.btn_Load = ttk.Button(
            self,
            text='Загрузить обработанные',
            command= lambda: self.cmd_CD_or_Load('Load'),
            width=23,
            state='disabled'
        )
        self.btn_CNL = ttk.Button( #Conclusions
            self,
            text='Файл с выводами и аннотациями',
            command=self.cmd_CNL,
            width=42
        )
        self.btn_Save = ttk.Button(
            self,
            text='Папка сохранения результатов',
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
            width=2,
            state='disabled'
        )
        self.btn_clean_CNL = ttk.Button(
            self,
            text='X',
            command=lambda: self.cmd_clean('CNL'),
            width=2,
            state='disabled'
        )
        self.btn_clean_Save = ttk.Button(
            self,
            text='X',
            command=lambda: self.cmd_clean('Save'),
            width=2,
            state='disabled'
        )
        self.widget_dict = {
            'btn_clean_all': self.btn_clean_all,
            'btn_CD': self.btn_CD,
            'btn_Load': self.btn_Load,
            'btn_CNL': self.btn_CNL,
            'btn_Save': self.btn_Save,
            'btn_clean_CD': self.btn_clean_CD,
            'btn_clean_CNL': self.btn_clean_CNL,
            'btn_clean_Save': self.btn_clean_Save,
            'l_CD_var': self.l_CD_var,
            'l_CNL_var': self.l_CNL_var,
            'l_Save_var': self.l_Save_var
        }
    
    def grid_inner_widgets(self):
        self.label_head.grid(column=1, row=0, columnspan=2, sticky='w')
        self.btn_clean_all.grid(column=0, row=1, rowspan=3, sticky='ns')
        self.btn_CD.grid(column=1, row=1, columnspan=2, sticky='we')
        #self.btn_Load.grid(column=2, row=1, sticky='we')
        self.btn_CNL.grid(column=1, row=2, columnspan=2, sticky='we')
        self.btn_Save.grid(column=1, row=3, columnspan=2, sticky='we')

        labels = (self.label_CD, self.label_CNL, self.label_Save)
        for row_id, label in enumerate(labels, start=1):
            label.grid(column=3, row=row_id, sticky='we')

        clean_btns = (
            self.btn_clean_CD, self.btn_clean_CNL, self.btn_clean_Save
        )
        for row_id, btn_clean in enumerate(clean_btns, start=1):
            btn_clean.grid(column=4, row=row_id, sticky='w')