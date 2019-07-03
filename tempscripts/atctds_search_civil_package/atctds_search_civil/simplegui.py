import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
import calendar
from datetime import date
from pathlib import Path
import _thread as thread

class FP1(ttk.Frame):
    def __init__(self, parent=tk.Tk(), **kwargs):
        ttk.Frame.__init__(self, parent, **kwargs)
        self.l_1_var = tk.StringVar()
        self.l_2_var = tk.StringVar()
        self.l_3_var = tk.StringVar()
        self.btn_CD = None
        self.btn_CNL = None
        self.btn_SV = None
        self.label_CD = None
        self.label_CNL = None
        self.label_SV = None
    
    def cmd_CD(self): #Court Desicions
        pass
    
    def cmd_CNL(self): #Conclusions
        pass
    
    def cmd_SV(self): #Save
        pass

    def build_widgets(self):
        self.btn_CD = ttk.Button( #Court Desicions
            self,
            text='Путь к суд.актам',
            command=self.cmd_CD,
            width=17
        )
        self.btn_CNL = ttk.Button( #Conclusions
            self,
            text='Путь к кирпичам',
            command=self.cmd_CNL,
            width=17
        )
        self.btn_SV = ttk.Button( #Save
            self,
            text='Путь сохранения',
            command=self.cmd_SV,
            width=17
        )
        self.label_CD = ttk.Label( #Court Desicions
            self,
            textvariable=self.l_1_var,
            anchor='w',
            width=100,
            relief='sunken'
        )
        self.label_CNL = ttk.Label( #Conclusions
            self,
            textvariable=self.l_2_var,
            anchor='w',
            width=100,
            relief='sunken'
        )
        self.label_SV = ttk.Label( #Save
            self,
            textvariable=self.l_3_var,
            anchor='w',
            width=100,
            relief='sunken'
        )
    
    def grid_inner_widgets(self):
        #self.grid(column=0, row=0, sticky='nwse')
        self.btn_CD.grid(column=0, row=0, sticky='w')
        self.btn_CNL.grid(column=0, row=1, sticky='w')
        self.btn_SV.grid(column=0, row=2, sticky='w')
        self.label_CD.grid(column=1, row=0, sticky='we')
        self.label_CNL.grid(column=1, row=1, sticky='we')
        self.label_SV.grid(column=1, row=2, sticky='we')
    
    def start_widget(self):
        self.build_widgets()
        self.grid_inner_widgets()
        self.mainloop()
    
    def start_widget_solo(self):
        self.build_widgets()
        self.grid_inner_widgets()
        self.grid(column=0, row=0, sticky='wnes')
        self.mainloop()
    




class FilePaths(ttk.Frame):
    def __init__(self, parent=None, **kwargs):
        ttk.Frame.__init__(self, parent, **kwargs)
        self.data = {
            'texts_folder_path': None,
            'path_to_raw_cnls': None,
            'res_folder_path': None
        }
        self.l_1_var = tk.StringVar()
        self.l_2_var = tk.StringVar()
        self.l_3_var = tk.StringVar()
        self.btn_1 = None
        self.btn_2 = None
        self.btn_3 = None
        self.label_1 = None
        self.label_2 = None
        self.label_3 = None
    
    def cmd_1(self):
        folder_path = fd.askdirectory()
        self.data['texts_folder_path'] = folder_path
        if len(folder_path) >= 100:
            folder_path = '...'+folder_path[-93:]
        self.l_1_var.set(folder_path)
    
    def cmd_2(self):
        file_path = fd.askopenfilename()
        self.data['path_to_raw_cnls'] = file_path
        if len(file_path) >= 100:
            file_path = '...'+file_path[-97:]
        self.l_2_var.set(file_path)
    
    def cmd_3(self):
        folder_path = fd.askdirectory()
        self.data['res_folder_path'] = folder_path
        if len(folder_path) >= 100:
            folder_path = '...'+folder_path[-93:]
        self.l_3_var.set(folder_path)
    
    def build_widgets(self):
        self.btn_1 = ttk.Button(
            self,
            text='Путь к суд.актам',
            command=self.cmd_1,
            width=17
        )
        self.btn_2 = ttk.Button(
            self,
            text='Путь к кирпичам',
            command=self.cmd_2,
            width=17
        )
        self.btn_3 = ttk.Button(
            self,
            text='Путь сохранения',
            command=self.cmd_3,
            width=17
        )
        self.label_1 = ttk.Label(
            self,
            textvariable=self.l_1_var,
            anchor='w',
            width=100,
            relief='sunken'
        )
        self.label_2 = ttk.Label(
            self,
            textvariable=self.l_2_var,
            anchor='w',
            width=100,
            relief='sunken'
        )
        self.label_3 = ttk.Label(
            self,
            textvariable=self.l_3_var,
            anchor='w',
            width=100,
            relief='sunken'
        )
    
    def grid_inner_widgets(self):
        #self.grid(column=0, row=0, sticky='nwse')
        self.btn_1.grid(column=0, row=0, sticky='w')
        self.btn_2.grid(column=0, row=1, sticky='w')
        self.btn_3.grid(column=0, row=2, sticky='w')
        self.label_1.grid(column=1, row=0, sticky='w')
        self.label_2.grid(column=1, row=1, sticky='w')
        self.label_3.grid(column=1, row=2, sticky='w')
        #self.grid(column=0, row=0, sticky='nwse')
        #self.columnconfigure(0, weight=1)
        #self.columnconfigure(1, weight=1)
    
    def start_widget(self):
        self.build_widgets()
        #self.grid(column=0, row=0, sticky='nwse')
        #self.columnconfigure(0, weight=1)
        #self.columnconfigure(1, weight=1)
        self.grid_inner_widgets()
        self.mainloop()