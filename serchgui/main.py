# https://stackoverflow.com/questions/10448882/how-do-i-set-a-minimum-window-size-in-tkinter
# useful info about setting minimum window size

from tkinter import *
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
        Scrollbar.set(self, lo, hi)
    def pack(self, **kw):
        raise "cannot use pack with this widget"
    def place(self, **kw):
        raise "cannot use place with this widget"

def f2():
    button_keys = (
        '01', '02', '11', '12', '21', '22'
    )
    label_keys = (
        '00', '10', '20'
    )
    old_settings = 'Старые настройки'
#########
    root = Tk()
#########
    menubar = Menu(root)
    root.config(menu=menubar)
    menubar.add_cascade(label='О программе')
#########   
    content = ttk.Frame(root)
    frames = {
        key:ttk.Frame(content) for key
        in ('concls', 'other', 'ctrl', 'processed', 'info', 'progbar')
    }
    buttons_concls = {
        key:ttk.Button(frames['concls']) for key in button_keys[:2]
    }
    labels_concls = {
        key:ttk.Label(frames['concls']) for key in (label_keys[0],)
    }
    #
    buttons_other = {
        key:ttk.Button(frames['other']) for key in (
            button_keys[:2]+button_keys[4:]
        )
    }
    labels_other = {
        key:ttk.Label(frames['other']) for key in label_keys
    }
    entries_other = {
        key:ttk.Entry(frames['other']) for key in button_keys[2:4]
    }
    #
    buttons_ctrl = {
        key:ttk.Button(frames['ctrl']) for key in button_keys[:2]
    }
    labels_ctrl = {
        key:ttk.Label(frames['ctrl']) for key in (label_keys[0],)
    }
    #
    labels_processed = {
        key:ttk.Label(frames['processed'], width=22) for key in ('00', '01')
    }
    #
    lstbox1 = Listbox(frames['concls'], relief='flat', height=15)
    scroll1 = AutoScrollbar(frames['concls'], orient='vertical', command=lstbox1.yview)
    lstbox1.configure(yscrollcommand=scroll1.set)
    #
    lstbox2 = Listbox(frames['processed'], relief='flat', height=18)
    scroll2 = AutoScrollbar(frames['processed'], orient='vertical', command=lstbox2.yview)
    lstbox2.configure(yscrollcommand=scroll2.set)
    #
    label_info = ttk.Label(frames['info'], text='Окно информации', width=22)
    text_info = Text(frames['info'], height=8, relief='flat', state='normal')
    scroll3 = AutoScrollbar(frames['info'], orient='vertical', command=text_info.yview)
    text_info.configure(yscrollcommand=scroll3.set)
    scroll4 = AutoScrollbar(frames['info'], orient='horizontal', command=text_info.xview)
    text_info.configure(xscrollcommand=scroll4.set)
    #
    progbar = ttk.Progressbar(
        frames['progbar'], orient='horizontal', mode='determinate'
    )
#########
    labels_concls['00'].configure(text='Выберите выводы', anchor='center')
    labels_other['00'].configure(text='Выберите данные', anchor='center')    
    labels_other['10'].configure(text='Выберите интервал', anchor='center')
    labels_other['20'].configure(text='Директория сохранения', anchor='center')
    labels_ctrl['00'].configure(text='Оценить судебные акты', anchor='center')
    labels_processed['00'].configure(text='Обработанные выводы', anchor='center')
    labels_processed['01'].configure(text='Fill by context', anchor='center')

    for dct in buttons_concls, buttons_other:
        for key in dct:
            if key[-1] == '1':
                dct[key].configure(text='Выбрать', width=22)
            elif key[-1] == '2':
                dct[key].configure(text='Старые настройки', width=22)    
    buttons_ctrl['01'].configure(text='Начать!', width=22)
    buttons_ctrl['02'].configure(text='Старые настройки!', width=22)

    content.configure(relief='flat', borderwidth=5)
    for frm in frames:
        frames[frm].configure(
            relief='groove', borderwidth=5
        )

#########
    content.grid(column=0, row=0, sticky='nwse')
    frames['concls'].grid(column=0, row=0, rowspan=3, sticky='nws')
    frames['other'].grid(column=1, row=0, sticky='nwse', padx=(10,10))
    frames['ctrl'].grid(column=1, row=1, sticky='nwse', padx=(10,10))
    frames['info'].grid(column=1, row=2, sticky='nwse', padx=(10,10))
    frames['processed'].grid(column=2, row=0, rowspan=3, sticky='nes')
    frames['progbar'].grid(column=0, row=3, columnspan=3, sticky='wse', pady=(5,0))
    #
    for key in buttons_concls:
        buttons_concls[key].grid(column=key[0], row=key[1], columnspan=2, sticky='nwse')
    for key in labels_concls:
        labels_concls[key].grid(column=key[0], row=key[1], columnspan=2, sticky='nwse')
    lstbox1.grid(column=0, row=3, sticky='nwse')
    scroll1.grid(column=1, row=3, sticky='ns')
    #
    for key in buttons_other:
        buttons_other[key].grid(column=key[0], row=key[1], sticky='nwse')
    for key in labels_other:
        labels_other[key].grid(column=key[0], row=key[1], sticky='nwse')
    for key in entries_other:
        entries_other[key].grid(column=key[0], row=key[1], sticky='we')
    #
    for key in buttons_ctrl:
        buttons_ctrl[key].grid(column=key[0], row=key[1], sticky='nwse')
    for key in labels_ctrl:
        labels_ctrl[key].grid(column=key[0], row=key[1], sticky='nwse')
    #
    label_info.grid(column=0, row=0, sticky='nwse')
    text_info.grid(column=0, row=1, sticky='nwse')
    scroll3.grid(column=1, row=1, sticky='ns')
    scroll4.grid(column=0, row=2, sticky='we')
    #
    for key in labels_processed:
        labels_processed[key].grid(column=key[0], row=key[1], columnspan=2, sticky='nwse')
    lstbox2.grid(column=0, row=1, sticky='nwse')
    scroll2.grid(column=1, row=1, sticky='ns')
    #
    progbar.grid(column=0, row=0, sticky='nwse')
#########
    root.update()
    root.minsize(root.winfo_width(), root.winfo_height())
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    content.columnconfigure(1, weight=1)
    content.rowconfigure(2, weight=1)
    frames['concls'].rowconfigure(3, weight=1)
    frames['processed'].rowconfigure(1, weight=1)
    frames['progbar'].columnconfigure(0, weight=1)
    frames['info'].columnconfigure(0, weight=1)
    frames['info'].rowconfigure(1, weight=1)

    root.mainloop()