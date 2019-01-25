#Treeview issue:
#https://stackoverflow.com/questions/49715456/forcing-a-tkinter-ttk-treeview-widget-to-resize-after-shrinking-its-column-width
#Bryan Oakley answer and index for his posts on stackoverflow.com:
#https://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter
#tkinter ttk.Entry validation:
#https://stackoverflow.com/questions/42332941/how-to-get-validation-to-work-in-tkinter-entry-fields
#https://stackoverflow.com/questions/4140437/interactively-validating-entry-widget-content-in-tkinter/4140988#4140988

import tkinter as tk
from tkinter import ttk
import calendar
from datetime import date
#leap yeasr formula:
#366 if ((year%4 == 0 and year%100 != 0) or (year%400 == 0)) else 365

from guidialogs import ffp, fdp

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
        self.info = None
        self.tv = None
        self.btn_1 = None
        self.data = None
        self.sort_flag_0 = False
        self.sort_flag_1 = False
        self.sort_flag_2 = False
    
    def btn_1_cmd(self):
        #print(self.tv.selection())
        if not self.tv.selection():
            return None
        for i in self.tv.selection():
            print(self.tv.item(i))

    def define(self, event):
        region = self.tv.identify('region', event.x, event.y)
        if region == 'heading':
            col = self.tv.identify('column', event.x, event.y)
            return col
    
    def sort0(self):
        self.tv.delete(*self.tv.get_children())
        self.data = sorted(self.data, key=lambda x: x[0], reverse=self.sort_flag_0)
        self.sort_flag_0 = not self.sort_flag_0
        for triple in self.data:
            key, val1, val2 = triple
            self.tv.insert(
                '',
                'end',
                text=key,
                values=(val1, val2)
            )
    
    def sort1(self):
        self.tv.delete(*self.tv.get_children())
        self.data = sorted(self.data, key=lambda x: x[1], reverse=self.sort_flag_1)
        self.sort_flag_1 = not self.sort_flag_1
        for triple in self.data:
            key, val1, val2 = triple
            self.tv.insert(
                '',
                'end',
                text=key,
                values=(val1, val2)
            )
    
    def sort2(self):
        self.tv.delete(*self.tv.get_children())
        self.data = sorted(self.data, key=lambda x: x[2], reverse=self.sort_flag_2)
        self.sort_flag_2 = not self.sort_flag_2
        for triple in self.data:
            key, val1, val2 = triple
            self.tv.insert(
                '',
                'end',
                text=key,
                values=(val1, val2)
            )

    def build_widget(self, head, cols, data):
        self.data = data
        self.btn_1 = ttk.Button(self, text='Print selected', command=self.btn_1_cmd)
        self.tv = ttk.Treeview(self, columns=cols)
        self.tv.heading('#0', text=head, command=self.sort0)
        self.tv.column('#0', width=100, stretch=True)
        for i, cmd in zip(cols, (self.sort1, self.sort2)):
            self.tv.heading(i, text=str(i), command=cmd)
            self.tv.column(i, width=40, stretch=True)
        for triple in data:
            key, val1, val2, = triple
            self.tv.insert(
                '',
                'end',
                text=key,
                values=(val1, val2)
            )
        #tv.bind('<Double-3>', lambda x: inner_f(x))
        #tv.bind('<Double-1>', lambda x: print(tv.item(tv.identify('item', x.x, x.y))))
        #tv.bind('<Double-2>', lambda x: print(tv.get_children('')))
        #tv.bind('<<TreeviewSelect>>', lambda x: print('Select!'))
        self.tv.bind(
            '<Double-1>',
            lambda x: print(self.tv.item(self.tv.identify('item', x.x, x.y)))
        )
        self.btn_1.pack(fill='x', expand='yes')
        self.tv.pack(fill='x', expand='yes')
    
    def start_widget(self):
        self.pack(fill='both', expand='yes')
        self.mainloop()


class Filesloader(ttk.Frame):
    def __init__(self, parent=None, **kwargs):
        ttk.Frame.__init__(self, parent, **kwargs)
        self.st_var = None
        self.btn_1 = None
        self.btn_r = None
        self.label_inf = None
        self.st_var = tk.StringVar()
    
    def btn_1_cmd(self):
        self.path = ffp()
        self.st_var.set(self.path)
        self.btn_1.configure(state='disabled')
        self.label_inf.update()
    
    def btn_r_cmd(self):
        for btn in self.btn_1, self.btn_r:
            btn.configure(state='normal')

    def build_widget(self):
        self.btn_1 = ttk.Button(
            self,
            text='Подгрузить данные о файле',
            command=self.btn_1_cmd
        )            
        self.btn_r = ttk.Button(
            self,
            text='Enable state!',
            command=self.btn_r_cmd
        )
        self.label_inf = ttk.Label(
            self,
            textvariable=self.st_var,
            background='pink',
            width=100
        )
        self.btn_1.pack(fill='x', expand='yes')
        self.label_inf.pack(fill='x', expand='yes')
        self.btn_r.pack(fill='x', expand='yes')
    
    def start_widget(self):
        self.pack(fill='both', expand='yes')
        self.mainloop()

class DateBox(tk.Frame):
    def __init__(self, parent=None, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        self.years = list(range(2016, 2020, 1))
        self.months_to_ints = {
            'Январь': 1, 'Февраль': 2, 'Март': 3, 'Апрель': 4,
            'Май': 5, 'Июнь': 6, 'Июль': 7, 'Август': 8,
            'Сентябрь': 9, 'Октябрь': 10, 'Ноябрь': 11, 'Декабрь': 12
        }
        self.months = [
            'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
            'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
            ]
        self.entr = None
        self.cmb_1 = None
        self.cmb_2 = None
        self.label = None
        self.label_inf = None
        self.label_inf_var = tk.StringVar(value='Введите год!')
        self.year_var = tk.StringVar()
        self.month_var = tk.StringVar()
        self.day_var = tk.StringVar()
    
    def validation_test(self, event):
        content = self.year_var.get()
        if (
            content.isdigit()
            and len(content) == 4
            and content[:3] == '201'
        ):
            self.entr.configure(state='readonly')
            for wdgt in self.cmb_1, self.cmb_2:
                wdgt.configure(state='normal')
            return True
        else:
            self.label_inf_var.set('Введите год, начиная с 2016')
    
    def month_range(self, event):
        month_code = self.cmb_1.current()+1
        self.month_var.set('{:0>2d}'.format(month_code))
        days_in_month = calendar.monthrange(
            int(self.year_var.get()),
            month_code
        )[1]
        self.cmb_2.configure(values=list(range(1, days_in_month+1, 1)))

    def convert_date(self, event):
        current_date = date(
            int(self.year_var.get()),
            self.cmb_1.current()+1,
            int(self.day_var.get())
        )
        print(current_date)
        self.current_date = current_date
    
    def build_widget(self):
        self.entr = ttk.Entry(
            self,
            textvariable=self.year_var,
        )
        self.entr.bind('<FocusOut>', self.validation_test)

        self.cmb_1 = ttk.Combobox(
            self,
            values=self.months
        )
        self.cmb_1.bind('<<ComboboxSelected>>', self.month_range)

        self.cmb_2 = ttk.Combobox(
            self,
            textvariable=self.day_var
        )
        self.cmb_2.configure(state='disabled')
        self.cmb_2.bind('<<ComboboxSelected>>', self.convert_date)

        self.label = ttk.Label(self, textvariable=self.label_inf_var)
        self.label_inf_y = ttk.Label(self, textvariable=self.year_var, anchor='center')
        self.label_inf_m = ttk.Label(self, textvariable=self.month_var, anchor='center')
        self.label_inf_d = ttk.Label(self, textvariable=self.day_var, anchor='center')
        self.label.pack(fill='x', expand='yes')
        self.entr.pack(fill='x', expand='yes')
        self.cmb_1.pack(fill='x', expand='yes')
        self.cmb_2.pack(fill='x', expand='yes')
        self.label_inf_d.pack(side='left', fill='x', expand='yes')
        self.label_inf_m.pack(side='left', fill='x', expand='yes')
        self.label_inf_y.pack(side='left', fill='x', expand='yes')
        self.label_inf_m = ttk.Label(self, textvariable=self.month_var)
    
    def start_widget(self):
        self.pack(fill='both', expand='yes')
        self.mainloop()


class InfoText(tk.Frame):
    def __init__(self, parent=None, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        self.text = None
        self.scroll = None
        self.btn_1 = None
    
    def btn_1_cmd(self):
        st = open
        #self.text.configure(state='normal')
        self.text.insert('1.0', st)
        #self.text.configure(state='disabled')
    
    def build_widget(self):
        self.text = tk.Text(self)#, state='disabled')
        self.scroll = AutoScrollbar(
            self,
            orient='vertical',
            command=self.text.yview
        )
        #self.scroll = ttk.Scrollbar(
        #    self,
        #    orient='vertical',
        #    command=self.text.yview
        #)
        self.text.configure(yscrollcommand=self.scroll.set)
        self.btn_1 = ttk.Button(self, text='Fill widget!', command=self.btn_1_cmd)
        self.text.grid(column=0, row=0, sticky='we')
        self.scroll.grid(column=1, row=0, sticky='nwse')
        self.btn_1.grid(column=2, row=1, sticky='we')
    
    def start_widget(self):
        self.grid(column=0, row=0, sticky='nwse')
        self.mainloop()