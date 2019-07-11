import tkinter as tk
from tkinter import ttk
import random as rd
from sys import argv

from iotext import MyReaderPre
from guidialogs import ffp, fdp

class Widget(ttk.Frame):
    def __init__(self, parent, **kwargs):
        ttk.Frame.__init__(self, parent, **kwargs)
        #self.start_widget(())

    def ccw(self):
        print('Widget.ccw', self.btn)
        options = ['sunken', 'flat', 'groove', 'raised', 'ridge']
        self.label.config(
            relief=options[rd.randint(0,4)]
        )
    
    def cba(self):
        print('Widget.cba', self.btn)
        options = [self.ccw, lambda: print('It\'s a dummy command!')]
        choise = options[rd.randint(0,1)] 
        print(choise)
        self.btn.config(
            command=choise
        )

    def build_widgets(self):
        self.label = ttk.Label(
            self,
            text='ПРИМЕР!'
        )
        self.btn = ttk.Button(
            self,
            text='Изменить рельеф',
            command=self.ccw,
            width=18,
            state='normal'
        )
        self.btn2 = ttk.Button(
            self,
            text='Вторая кнопка',
            command=self.cba,
            width=18
        )
        self.label2 = ttk.Label(
            self,
            text='Подвал'
        )

    def grid_widgets(self):
        self.label.grid(column=0, row=0, sticky='nwes')
        self.btn.grid(column=1, row=0, sticky='nwes')
        self.label2.grid(column=0, row=1, sticky='nwes')
        self.btn2.grid(column=1, row=1, sticky='nwes')
    
    def start_widget(self):
        self.build_widgets()
        self.grid_widgets()
        print('Widget.start_widget:', 'widgets initialized and grinded!')

class Wrapper(Widget):
    def __init__(self, parent):
        Widget.__init__(self, parent)

class Compound(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.inner_frame = Wrapper(self)
        self.inner_frame.start_widget()

class ML(Compound):
    def __init__(self, parent):
        Compound.__init__(self, parent)
        self.change_command()
    
    def change_relief(self):
        print('ML.change_relief', self.inner_frame.btn)
        options = ['sunken', 'flat', 'groove', 'raised', 'ridge']
        self.inner_frame.label.config(
            relief=options[rd.randint(0,4)]
        )
    
    def change_command(self):
        print('ML.change_command', self.inner_frame.btn)
        print(self.inner_frame.btn)
        self.inner_frame.btn2['command'] = self.change_relief

    def start_widget_solo(self):
        self.inner_frame.grid(column=0, row=0, sticky='wnse')
        self.grid(column=0, row=0, sticky='nwse')
        self.mainloop()


if __name__ == '__main__':
    print(argv)
    mode = argv[1]
    if mode == '1':
        print('Widget class')
        w = Widget(tk.Tk())
        w.start_widget()
        w.grid(column=0, row=0, sticky='wnse')
        w.mainloop()
    elif mode == '2':
        print('ML class')
        ml = ML(tk.Tk())
        ml.start_widget_solo()


