# https://stackoverflow.com/questions/10448882/how-do-i-set-a-minimum-window-size-in-tkinter
# useful info about setting minimum window size

import tkinter as tk
from tkinter import ttk

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

class MyGUI():
    def __init__(self):
        self.root = None
        self.menubar = None
        self.content = None
        self.frames = None
        self.progbar = None
        self.buttons_concls = None
        self.labels_concls = None
        self.buttons_other = None
        self.labels_other = None
        self.entries_other = None
        self.buttons_ctrl = None
        self.labels_ctrl = None
        self.labels_processed = None
        self.lstbox1 = None
        self.scroll1 = None
        self.lstbox2 = None
        self.scroll2 = None
        self.label_info = None
        self.scroll3 = None
        self.scroll4 = None
        self.text_info = None
        self.start_app()
    
    def define_widgets(self):
        self.root = tk.Tk()
        button_keys = (
            '01', '02', '11', '12', '21', '22'
        )
        label_keys = (
            '00', '10', '20'
        )
    #########
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        self.menubar.add_cascade(label='Добавить файлы')
        self.menubar.add_cascade(label='О программе')
    #########
        self.content = ttk.Frame(self.root)
        self.frames = {
            key:ttk.Frame(self.content) for key
            in ('concls', 'other', 'ctrl', 'processed', 'info', 'progbar')
        }
        self.buttons_concls = {
            key:ttk.Button(self.frames['concls']) for key in button_keys[:2]
        }
        self.labels_concls = {
            key:ttk.Label(self.frames['concls']) for key in (label_keys[0],)
        }
        #
        self.buttons_other = {
            key:ttk.Button(self.frames['other']) for key in (
                button_keys[:2]+button_keys[4:]
            )
        }
        self.labels_other = {
            key:ttk.Label(self.frames['other']) for key in label_keys
        }
        self.entries_other = {
            key:ttk.Entry(self.frames['other']) for key in button_keys[2:4]
        }
        #
        self.buttons_ctrl = {
            key:ttk.Button(self.frames['ctrl']) for key in button_keys[:2]
        }
        self.labels_ctrl = {
            key:ttk.Label(self.frames['ctrl']) for key in (label_keys[0],)
        }
        #
        self.labels_processed = {
            key:ttk.Label(self.frames['processed'], width=22) for key in ('00', '01')
        }
        #
        self.lstbox1 = tk.Listbox(self.frames['concls'], relief='flat', height=15)
        self.scroll1 = AutoScrollbar(self.frames['concls'], orient='vertical', command=self.lstbox1.yview)
        self.lstbox1.configure(yscrollcommand=self.scroll1.set)
        #
        self.lstbox2 = tk.Listbox(self.frames['processed'], relief='flat', height=18)
        self.scroll2 = AutoScrollbar(self.frames['processed'], orient='vertical', command=self.lstbox2.yview)
        self.lstbox2.configure(yscrollcommand=self.scroll2.set)
        #
        self.label_info = ttk.Label(self.frames['info'], text='Окно информации', width=22)
        self.text_info = tk.Text(self.frames['info'], height=8, relief='flat', state='normal')
        self.scroll3 = AutoScrollbar(self.frames['info'], orient='vertical', command=self.text_info.yview)
        self.text_info.configure(yscrollcommand=self.scroll3.set)
        self.scroll4 = AutoScrollbar(self.frames['info'], orient='horizontal', command=self.text_info.xview)
        self.text_info.configure(xscrollcommand=self.scroll4.set)
        #
        self.progbar = ttk.Progressbar(
            self.frames['progbar'], orient='horizontal', mode='determinate'
        )
        ##########
        self.labels_concls['00'].configure(text='Выберите выводы', anchor='center')
        self.labels_other['00'].configure(text='Папка с судами', anchor='center')    
        self.labels_other['10'].configure(text='Временной интервал', anchor='center')
        self.labels_other['20'].configure(text='Директория сохранения', anchor='center')
        self.labels_ctrl['00'].configure(text='Оценить судебные акты', anchor='center')
        self.labels_processed['00'].configure(text='Обработанные выводы', anchor='center')
        self.labels_processed['01'].configure(text='Fill by context', anchor='center')
        #
        for dct in self.buttons_concls, self.buttons_other:
            for key in dct:
                if key[-1] == '1':
                    dct[key].configure(text='Выбрать', width=22)
                elif key[-1] == '2':
                    dct[key].configure(text='Старые настройки', width=22)    
        self.buttons_ctrl['01'].configure(text='Начать!', width=22)
        self.buttons_ctrl['02'].configure(text='Старые настройки!', width=22)
        #
        self.content.configure(relief='flat', borderwidth=5)
        for frm in self.frames:
            self.frames[frm].configure(
                relief='groove', borderwidth=5
            )
    
    def grid_widgets(self):
        self.content.grid(column=0, row=0, sticky='nwse')
        self.frames['concls'].grid(column=0, row=0, rowspan=3, sticky='nws')
        self.frames['other'].grid(column=1, row=0, sticky='nwse', padx=(10,10))
        self.frames['ctrl'].grid(column=1, row=1, sticky='nwse', padx=(10,10))
        self.frames['info'].grid(column=1, row=2, sticky='nwse', padx=(10,10))
        self.frames['processed'].grid(column=2, row=0, rowspan=3, sticky='nes')
        self.frames['progbar'].grid(column=0, row=3, columnspan=3, sticky='wse', pady=(5,0))
        #
        for key in self.buttons_concls:
            self.buttons_concls[key].grid(column=key[0], row=key[1], columnspan=2, sticky='nwse')
        for key in self.labels_concls:
            self.labels_concls[key].grid(column=key[0], row=key[1], columnspan=2, sticky='nwse')
        #
        self.lstbox1.grid(column=0, row=3, sticky='nwse')
        self.scroll1.grid(column=1, row=3, sticky='ns')
        #
        for key in self.buttons_other:
            self.buttons_other[key].grid(column=key[0], row=key[1], sticky='nwse')
        for key in self.labels_other:
            self.labels_other[key].grid(column=key[0], row=key[1], sticky='nwse')
        for key in self.entries_other:
            self.entries_other[key].grid(column=key[0], row=key[1], sticky='we')
        #
        for key in self.buttons_ctrl:
            self.buttons_ctrl[key].grid(column=key[0], row=key[1], sticky='nwse')
        for key in self.labels_ctrl:
            self.labels_ctrl[key].grid(column=key[0], row=key[1], sticky='nwse')
        #
        self.label_info.grid(column=0, row=0, sticky='nwse')
        self.text_info.grid(column=0, row=1, sticky='nwse')
        self.scroll3.grid(column=1, row=1, sticky='ns')
        self.scroll4.grid(column=0, row=2, sticky='we')
        #
        for key in self.labels_processed:
            self.labels_processed[key].grid(column=key[0], row=key[1], columnspan=2, sticky='nwse')
        #
        self.lstbox2.grid(column=0, row=1, sticky='nwse')
        self.scroll2.grid(column=1, row=1, sticky='ns')
        #
        self.progbar.grid(column=0, row=0, sticky='nwse')
        #########
        self.root.minsize(self.root.winfo_width(), self.root.winfo_height())
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.content.columnconfigure(1, weight=1)
        self.content.rowconfigure(2, weight=1)
        self.frames['concls'].rowconfigure(3, weight=1)
        self.frames['processed'].rowconfigure(1, weight=1)
        self.frames['progbar'].columnconfigure(0, weight=1)
        self.frames['info'].columnconfigure(0, weight=1)
        self.frames['info'].rowconfigure(1, weight=1)

        self.root.mainloop()
    
    def start_app(self):
        self.define_widgets()
        self.grid_widgets()