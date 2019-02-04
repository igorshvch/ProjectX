#Treeview issue:
#https://stackoverflow.com/questions/49715456/forcing-a-tkinter-ttk-treeview-widget-to-resize-after-shrinking-its-column-width
#Bryan Oakley answer and index for his posts on stackoverflow.com:
#https://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter
#tkinter ttk.Entry validation:
#https://stackoverflow.com/questions/42332941/how-to-get-validation-to-work-in-tkinter-entry-fields
#https://stackoverflow.com/questions/4140437/interactively-validating-entry-widget-content-in-tkinter/4140988#4140988

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
import calendar
from datetime import date
from pathlib import Path
import random
import _thread as thread
#leap yeasr formula:
#366 if ((year%4 == 0 and year%100 != 0) or (year%400 == 0)) else 365

#from guidialogs import ffp, fdp
from tempscripts import tempmain as tpm
from textproc import rwtools, conclprep as cnp

lock = thread.allocate_lock()

PATHS = {
    'НДС': r'C:\Users\EA-ShevchenkoIS\ProjectX\CommonData\PPN\PPN_4.txt',
    'НП': r'C:\Users\EA-ShevchenkoIS\ProjectX\CommonData\PPN\PPN_9.txt',
    'НДФЛ_СВ': r'C:\Users\EA-ShevchenkoIS\ProjectX\CommonData\PPN\PPN_31.txt',
    'Ч1_НК': r'C:\Users\EA-ShevchenkoIS\ProjectX\CommonData\PPN\PPN_34.txt',
    'stpw': (
        r'C:\Users\EA-ShevchenkoIS\ProjectX\CommonData\custom_stpw_wo_objections'
    ),
    'patterns': r'C:\Users\EA-ShevchenkoIS\ProjectX\patterns.txt'
}

DIR_STRUCT = {
    'НДС': ['НДС', 'НДС/Результат'],
    'НП': ['НП', 'НП/Результат'],
    'НДФЛ_СВ': ['НДФЛ_СВ', 'НДФЛ_СВ/Результат'],
    'Ч1_НК': ['Ч1_НК', 'Ч1_НК/Результат']
}

class AutoScrollbar(ttk.Scrollbar):
    # http://effbot.org/zone/tkinter-autoscrollbar.htm
    # a scrollbar that hides itself if it's not needed.  only
    # works if you use the grid geometry manager.
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            # grid_remove is currently missing from Tkinter!
            self.tk.call("grid", "remove", self)
        else:
            self.grid()
        ttk.Scrollbar.set(self, lo, hi)
    def pack(self, **kw):
        raise "cannot use pack with this widget"
    def place(self, **kw):
        raise "cannot use place with this widget"


class TreeviewBuilder(ttk.Frame):
    def __init__(self, parent=None, **kwargs):
        ttk.Frame.__init__(self, parent, **kwargs)
        self.data = {}
        self.info = None
        self.tv = None
        self.btn_1 = None
        self.sort_flag_0 = False
        self.sort_flag_1 = False
        self.sort_flag_2 = False
        self.counter = tk.IntVar()

    def define(self, event):
        region = self.tv.identify('region', event.x, event.y)
        if region == 'heading':
            col = self.tv.identify('column', event.x, event.y)
            return col
    
    def sort0(self):
        items = []
        for i in self.tv.get_children():
            cnl = self.tv.item(i)['text']
            code = self.tv.item(i)['values'][0]
            items.append((cnl, code))
        self.tv.delete(*self.tv.get_children())
        items = sorted(items, key=lambda x: x[0], reverse=self.sort_flag_0)
        self.sort_flag_0 = not self.sort_flag_0
        for pair in items:
            key, val1 = pair
            self.tv.insert(
                '',
                'end',
                text=key,
                values=(val1,)
            )

    def sort1(self):
        items = []
        for i in self.tv.get_children():
            cnl = self.tv.item(i)['text']
            code = self.tv.item(i)['values'][0]
            items.append((cnl, code))
        self.tv.delete(*self.tv.get_children())
        items = sorted(items, key=lambda x: x[1], reverse=self.sort_flag_0)
        self.sort_flag_0 = not self.sort_flag_0
        for pair in items:
            key, val1 = pair
            self.tv.insert(
                '',
                'end',
                text=key,
                values=(val1,)
            )

    def build_widgets(self):
        #cols = ('ЭСС', 'Актуален?')
        cols = ('ЭСС',)

        self.btn_1 = ttk.Button(
            self,
            text='Загрузить кирпичи',
            command= lambda: print('Command not specified!'),
            state='disabled'
        )
        self.btn_2 = ttk.Button(
            self,
            text='Подготовить выводы',
            command= lambda: print('Command not specified!'),
            state='disabled'
        )

        self.label_inf = ttk.Label(
            self,
            textvariable=self.counter,
            width=4,
            anchor='e',
            relief='sunken'
        )
        #self.btn_2 = ttk.Button(
        #    self,
        #    text='Подробнее',
        #    command=self.btn_2_cmd
        #)

        self.tv = ttk.Treeview(self, columns=cols)
        self.tv.heading('#0', text='Кирпич', command=self.sort0)
        self.tv.column('#0', width=100, stretch=True)
        for i, cmd in zip(cols, (self.sort1, )):#self.sort2)):
            self.tv.heading(i, text=str(i), command=cmd)
            self.tv.column(i, width=65, stretch=True)
        #tv.bind('<Double-3>', lambda x: inner_f(x))
        #tv.bind('<Double-1>', lambda x: print(tv.item(tv.identify('item', x.x, x.y))))
        #tv.bind('<Double-2>', lambda x: print(tv.get_children('')))
        #tv.bind('<<TreeviewSelect>>', lambda x: print('Select!'))
        self.tv.bind(
            '<Double-1>',
            lambda x: print(self.tv.item(self.tv.identify('item', x.x, x.y)))
        )
        self.scroll = AutoScrollbar(
                    self,
                    orient='vertical',
                    command=self.tv.yview
                )
        self.tv.configure(yscrollcommand=self.scroll.set)
    
    def grid_inner_widgets(self):
        self.tv.grid(column=0, row=0, columnspan=2, sticky='we')
        self.btn_1.grid(column=0, row=1, sticky='we')
        self.btn_2.grid(column=0, row=2, columnspan=2, sticky='we')
        self.label_inf.grid(column=1, row=1, sticky='we')
        self.scroll.grid(column=2, row=0, sticky='nes')
    
    def start_widget(self):
        self.build_widgets()
        self.grid_inner_widgets()
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


class DateBox(ttk.Frame):
    def __init__(self, parent=None, **kwargs):
        ttk.Frame.__init__(self, parent, **kwargs)
        self.data = {
            'year': None,
            'month': None,
            'day': None
        }
        self.years = list(range(2017, 2020, 1))
        self.months_to_ints = {
            'Январь': 1, 'Февраль': 2, 'Март': 3, 'Апрель': 4,
            'Май': 5, 'Июнь': 6, 'Июль': 7, 'Август': 8,
            'Сентябрь': 9, 'Октябрь': 10, 'Ноябрь': 11, 'Декабрь': 12
        }
        self.months = [
            'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
            'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
            ]
        self.cmb_1 = None
        self.cmb_2 = None
        self.cmb_3 = None
        self.label_h = None
        self.year_var = tk.StringVar()
        self.month_var = tk.StringVar()
        self.day_var = tk.StringVar()
    
    def store_year(self, event):
        year = int(self.year_var.get())
        self.data['year'] = year
        self.cmb_2.configure(state='normal')
        if self.data['month'] and self.data['day']:
            print(
                '{:4d}-{:0>2d}-{:0>2d}'.format(
                    self.data['year'],
                    self.data['month'],
                    self.data['day']
                )
            )
    
    def store_month(self, event):
        month_code = self.cmb_2.current()+1
        self.data['month'] = month_code
        self.month_var.set('{:0>2d}.'.format(month_code))
        days_in_month = calendar.monthrange(
            self.data['year'],
            self.data['month']
        )[1]
        self.cmb_3.configure(
            values=list(range(1, days_in_month+1, 1)),
            state='normal'
        )
        if self.data['day']:
            print(
                '{:4d}-{:0>2d}-{:0>2d}'.format(
                    self.data['year'],
                    self.data['month'],
                    self.data['day']
                )
            )

    def store_day(self, event):
        day_code = self.cmb_3.current()+1
        self.data['day'] = day_code
        self.day_var.set('{:0>2d}.'.format(day_code))
        print(
            '{:4d}-{:0>2d}-{:0>2d}'.format(
                self.data['year'],
                self.data['month'],
                self.data['day']
            )
        )
    
    def build_widgets(self):
        self.cmb_1 = ttk.Combobox(
            self,
            values=('2017', '2018', '2019'),
            textvariable=self.year_var,
            width=10
        )
        self.cmb_1.bind('<<ComboboxSelected>>', self.store_year)

        self.cmb_2 = ttk.Combobox(
            self,
            values=self.months,
            width=10,
            state='disabled'
        )
        self.cmb_2.bind('<<ComboboxSelected>>', self.store_month)

        self.cmb_3 = ttk.Combobox(
            self,
            width=10,
            state='disabled'
        )
        self.cmb_3.bind('<<ComboboxSelected>>', self.store_day)

        self.label_h = ttk.Label(self, text='Дата', anchor='center')
        self.label_inf_y = ttk.Label(
            self,
            textvariable=self.year_var,
            anchor='w',
            width=4,
            relief='sunken'
        )
        self.label_inf_m = ttk.Label(
            self,
            textvariable=self.month_var,
            anchor='center',
            width=3,
            relief='sunken'
        )
        self.label_inf_d = ttk.Label(
            self,
            textvariable=self.day_var,
            anchor='e',
            width=3,
            relief='sunken'
        )
    
    def grid_inner_widgets(self):
        #self.grid(column=0, row=0, sticky='nwse')
        self.label_h.grid(column=0, row=0, columnspan=3, sticky='we')
        self.cmb_1.grid(column=0, row=1, columnspan=3, sticky='we')
        self.cmb_2.grid(column=0, row=2, columnspan=3, sticky='we')
        self.cmb_3.grid(column=0, row=3, columnspan=3, sticky='we')
        self.label_inf_d.grid(column=0, row=4, sticky='w')
        self.label_inf_m.grid(column=1, row=4, sticky='w')
        self.label_inf_y.grid(column=2, row=4, sticky='w')
        #self.columnconfigure(0, weight=1)
        #self.columnconfigure(1, weight=1)
        #self.columnconfigure(2, weight=1)
    
    def start_widget(self):
        self.build_widgets()
        self.grid(column=0, row=0, sticky='nwse')
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.grid_inner_widgets()
        self.mainloop()


class InfoText(ttk.Frame):
    def __init__(self, parent=None, **kwargs):
        ttk.Frame.__init__(self, parent, **kwargs)
        self.data = {}
        self.text = None
        self.scroll = None
        self.btn_1 = None
    
    #def btn_1_cmd(self):
    #    with open(ffp(), mode='r') as file:
    #        st = file.read()
    #    st = st.replace('\n', '\n\t')
    #    self.text.configure(state='normal')
    #    self.text.insert('1.0', st)
    #    self.text.configure(state='disabled')
    
    def build_widgets(self):
        self.text = tk.Text(self, state='disabled')
        self.scroll = AutoScrollbar(
            self,
            orient='vertical',
            command=self.text.yview
        )
        self.text.configure(yscrollcommand=self.scroll.set)
    
    def grid_inner_widgets(self):
        #self.grid(column=0, row=0, sticky='nwse')
        self.text.grid(column=0, row=0, sticky='nwse')
        self.scroll.grid(column=1, row=0, sticky='nes')
        #self.columnconfigure(0, weight=1)
        #self.columnconfigure(1, weight=1)
        #self.rowconfigure(0, weight=1)
    
    def start_widget(self):
        self.build_widgets()
        self.grid_inner_widgets()
        self.mainloop()


class UpperRightButtons(ttk.Frame):
    def __init__(self, parent=None, **kwargs):
        ttk.Frame.__init__(self, parent, **kwargs)
        self.data = {}
        self.btn_1 = None
    
    def cmd_1(self):
        print('Command not specified!')

    def build_widgets(self):
        self.btn_1 = ttk.Button(
            self,
            text='Подготовить акты',
            command=self.cmd_1
        )
    
    def grid_inner_widgets(self):
        self.btn_1.grid(column=0, row=0, sticky='e')

    def start_widget(self):
        pass


class LowerLeftBottons(ttk.Frame):
    def __init__(self, parent=None, **kwargs):
        ttk.Frame.__init__(self, parent, **kwargs)
        self.data = {}
        self.btn_1 = None
    
    def cmd_1(self):
        print('Command not specified!')

    def build_widgets(self):
        self.btn_1 = ttk.Button(
            self,
            text='Подготовить акты',
            state='disabled',
            command=self.cmd_1,
            width=17
        )
        self.btn_2 = ttk.Button(
            self,
            text='Сделать добор',
            state='disabled',
            command=self.cmd_1,
            width=17
        )
    
    def grid_inner_widgets(self):
        self.btn_1.grid(column=0, row=0, sticky='nw')
        self.btn_2.grid(column=0, row=1, sticky='nw')

    def start_widget(self):
        pass


class MainLogic():
    def __init__(self):
        self.root = tk.Tk()
        self.data = {}
        self.files = {}
        self.res = {}
    
    def build_widgets(self):
        root = self.root
        self.wdgts = {
            'tv': TreeviewBuilder(root),
            'fp': FilePaths(root),
            'db': DateBox(root),
            'it': InfoText(root),
            #'urb': UpperRightButtons(root),
            'llb': LowerLeftBottons(root)
        }
        for key in self.wdgts:
            self.data[key] = self.wdgts[key].data
            self.wdgts[key].build_widgets()
            self.wdgts[key].grid_inner_widgets()
        self.reconfigure()
        self.wdgts['fp'].grid(column=0, row=0, columnspan=2, sticky='we')
        #self.wdgts['urb'].grid(column=2, row=0, sticky='ne')
        self.wdgts['tv'].grid(column=0, row=1, sticky='n')
        self.wdgts['db'].grid(column=0, row=2, sticky='wne')
        self.wdgts['llb'].grid(column=0, row=3, sticky='wn')
        self.wdgts['it'].grid(column=1, row=1, rowspan=4, sticky='nwse')
        self.wdgts['it'].columnconfigure(0, weight=1)
        self.wdgts['it'].rowconfigure(0, weight=1)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(3, weight=1)
        root.update()
        root.minsize(root.winfo_width(), root.winfo_height())
        self.root.mainloop()
    
    def reconfigure(self):
        self.wdgts['fp'].btn_1.configure(command=self.def_path_to_docs)
        self.wdgts['fp'].btn_2.configure(command=self.def_path_to_concls)
        self.wdgts['fp'].btn_3.configure(command=self.def_path_to_save)
        self.wdgts['tv'].btn_1.configure(command=self.upload_concls)
        self.wdgts['tv'].btn_2.configure(command=self.prepare_concls)
        self.wdgts['tv'].tv.bind(
            '<Double-1>',
            lambda x: self.special_tv_insert(x)
        )
        self.wdgts['db'].cmb_1.bind(
            '<<ComboboxSelected>>',
            lambda x: self.print_date(x, 'year')
        )
        self.wdgts['db'].cmb_2.bind(
            '<<ComboboxSelected>>',
            lambda x: self.print_date(x, 'month')
        )
        self.wdgts['db'].cmb_3.bind(
            '<<ComboboxSelected>>',
            lambda x: self.print_date(x, 'day')
        )
        self.wdgts['llb'].btn_1.configure(
            command=lambda: thread.start_new_thread(self.prepare_acts, ())
        )
        self.wdgts['llb'].btn_2.configure(
            command=lambda: thread.start_new_thread(self.find_similar, ())
        )

    def upload_concls(self):
        self.wdgts['tv'].tv.delete(*self.wdgts['tv'].tv.get_children())
        if not self.data['fp']['path_to_raw_cnls']:
            print('Set path to concls!')
            return None
        with open(self.data['fp']['path_to_raw_cnls'], mode='r') as f:
            concls = f.read()
        concls = tpm.text_to_tuples(concls)
        for pair in concls:
            cnl, code = pair
            self.wdgts['tv'].tv.insert(
                '',
                'end',
                text=cnl,
                values=(code,)#
            )
        self.wdgts['tv'].counter.set(len(self.wdgts['tv'].tv.get_children()))
        self.wdgts['tv'].btn_2.configure(state='normal')
        self.res['raw_concls'] = concls
    
    def prepare_concls(self):
        if not self.data['fp']['path_to_raw_cnls']:
            print('Set path to concls!')
            return None
        raw_cnl = {'НДС': '', 'НП': '', 'НДФЛ_СВ': '', 'Ч1_НК': ''}
        for cnl, code in self.res['raw_concls']:
            raw_cnl[code] += (cnl+'\n')
        stored_cnl = {key: None for key in raw_cnl}
        for key in stored_cnl:
            stored_cnl[key] = rwtools.read_text(
                PATHS[key], encoding='utf_8_sig'
            )
        prep_cnl = {
            code: cnp.find_concls_2(raw_cnl[code][:-1], stored_cnl[code])
            for code in raw_cnl
        }
        self.res['prep_concls'] = prep_cnl
        self.insert_info('Выводы подготовлены для добора!')
    
    def print_date(self, event, mode):
        if mode == 'year':
            self.wdgts['db'].store_year(None)
        elif mode == 'month':
            self.wdgts['db'].store_month(None)
        elif mode == 'day':
            self.wdgts['db'].store_day(None)
        if self.data['db']['month'] and self.data['db']['day']:
            year, month, day = (
                self.data['db']['year'],
                self.data['db']['month'],
                self.data['db']['day']
            )
            date = '{:0>2d}.{:0>2d}.{:4d}'.format(day, month, year)
            self.res['date'] = [year, month, day]
            self.res['date_text'] = '{:4d}-{:0>2d}-{:0>2d}'.format(
                year, month, day
            )
            self.insert_info(
                'Искать акты, загруженные в КонсультантПлюс позже {}'.format(
                    date
                )
            )
            if self.data['fp']['texts_folder_path']:
                self.wdgts['llb'].btn_1.configure(state='normal')
            if self.data['fp']['res_folder_path']:
                self.create_sub_dirs()
    
    def create_sub_dirs(self):
        info_text = 'Сформированы папки для сохранения:'
        root = Path(self.data['fp']['res_folder_path']).joinpath(
            'После_'+self.res['date_text']
        )
        self.res['save_dirs'] = {}
        for key in DIR_STRUCT:
            self.res['save_dirs'][key] = []
            for item in DIR_STRUCT[key]:
                dir_path = root.joinpath(item)
                self.res['save_dirs'][key].append(dir_path)
                dir_path.mkdir(parents=True, exist_ok=True)
                info_text += '\n{}'.format(dir_path)
        self.insert_info(info_text)

    def def_path_to_docs(self):
        self.wdgts['fp'].cmd_1()
        #self.wdgts['llb'].btn_1.configure(state='normal')
    
    def def_path_to_concls(self):
        self.wdgts['fp'].cmd_2()
        self.wdgts['tv'].btn_1.configure(state='normal')
    
    def def_path_to_save(self):
        self.wdgts['fp'].cmd_3()
        if self.res.get('date') and self.data['fp']['res_folder_path']:
            self.create_sub_dirs()
        ########################

    def prepare_acts(self):
        for wdgt in (
            self.wdgts['fp'].btn_1,
            self.wdgts['fp'].btn_2,
            self.wdgts['fp'].btn_3,
            self.wdgts['tv'].btn_1,
            self.wdgts['tv'].btn_2,
            self.wdgts['db'].cmb_1,
            self.wdgts['db'].cmb_2,
            self.wdgts['db'].cmb_3,
            self.wdgts['llb'].btn_1
        ):
            wdgt.configure(state='disabled')
        self.res['doc_gen'] = {}
        self.res['pkl'] = {}
        self.res['lem_map'] = {}
        year, month, day = self.res['date']
        with lock:
            self.insert_info('Читаю акты!')
        for code in self.res['save_dirs']:
            self.res['doc_gen'][code] = tpm.create_doc_gen(
                self.data['fp']['texts_folder_path'],
                PATHS['patterns'],
                code,
                year, month, day
            )
        with lock:
            self.insert_info('Обрабатываю текст, формирую словари!')
        for code in self.res['doc_gen']:
            self.res['pkl'][code] = tpm.create_pkl(
                self.res['save_dirs'][code][0].joinpath('pkl'),
                self.res['doc_gen'][code]
            )
            self.res['lem_map'][code] = tpm.create_and_save_lem_map(
                self.res['save_dirs'][code][0],
                self.res['pkl'][code],
                code
            )
        for wdgt in (
            self.wdgts['fp'].btn_1,
            self.wdgts['fp'].btn_2,
            self.wdgts['fp'].btn_3,
            self.wdgts['tv'].btn_1,
            self.wdgts['tv'].btn_2,
            self.wdgts['db'].cmb_1,
            self.wdgts['db'].cmb_2,
            self.wdgts['db'].cmb_3,
            #self.wdgts['llb'].btn_1
        ):
            wdgt.configure(state='normal')
        with lock:
            self.insert_info('Судебные акты подготовлены для добора')
        self.wdgts['llb'].btn_2.configure(state='normal')
    
    def find_similar(self):
        for wdgt in (
            self.wdgts['fp'].btn_1,
            self.wdgts['fp'].btn_2,
            self.wdgts['fp'].btn_3,
            self.wdgts['tv'].btn_1,
            self.wdgts['tv'].btn_2,
            self.wdgts['db'].cmb_1,
            self.wdgts['db'].cmb_2,
            self.wdgts['db'].cmb_3,
            #self.wdgts['llb'].btn_1,
            self.wdgts['llb'].btn_2
        ):
            wdgt.configure(state='disabled')
        stpw = rwtools.load_pickle(PATHS['stpw'])
        for code in self.res['prep_concls']:
            with lock:
                self.insert_info('Обрабатываю выводы из ЭСС {}'.format(code))
            tpm.map_docs_to_concls_2(
                self.res['pkl'][code],
                self.res['lem_map'][code],
                self.res['prep_concls'][code],
                stpw,
                self.res['save_dirs'][code][0],
                self.res['save_dirs'][code][1],
                code,
                func=self.insert_info
            )
        for wdgt in (
            self.wdgts['fp'].btn_1,
            self.wdgts['fp'].btn_2,
            self.wdgts['fp'].btn_3,
            self.wdgts['tv'].btn_1,
            self.wdgts['tv'].btn_2,
            self.wdgts['db'].cmb_1,
            self.wdgts['db'].cmb_2,
            self.wdgts['db'].cmb_3,
            #self.wdgts['llb'].btn_1,
            #self.wdgts['llb'].btn_2
        ):
            wdgt.configure(state='normal')
        with lock:
            self.insert_info('Добор завершен!')   

    def insert_info(self, text):
        self.wdgts['it'].text.configure(state='normal')
        text = '\t'+str(text)+'\n'+'='*69+'\n'
        self.wdgts['it'].text.insert('end', text)
        self.wdgts['it'].text.configure(state='disabled')
    
    def special_tv_insert(self, x):
        data = self.wdgts['tv'].tv.item(
            self.wdgts['tv'].tv.identify('item', x.x, x.y)
        )
        val1 = data['values'][0] if data['values'] else 'Заголовок'
        val2 = data['text'] if data['text'] else 'Текст заголовка'
        text = val1+'\n\t'+val2
        self.insert_info(text)

    #def start_widget(self):
    #    self.root.mainloop()