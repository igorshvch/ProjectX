import sys
import tkinter as tk
from tkinter import ttk

from atctds_search_civil import debugger as dbg

class CommonInterface():
    def __init__(self, tk_parent):
        self.tk_parent = tk_parent
        self.widget_dict = {}
        self.widget_flag = False
    
    def re(self, key):
        '''
        Internal acting function providing 'dict()'-like interface
        to access and retrieve inner widgets of particluar
        tk.Frame subclass
        '''
        return self.widget_dict[key]
    
    @dbg.method_speaker('Empty method! For internal use only!')
    def load_external_data(self, data=None):
        return None

    @dbg.method_speaker('Empty method! For internal use only!')
    def extract_internal_data(self):
        return None
    
    @dbg.method_speaker('Empty method! For internal use only!')
    def build_widgets(self):
        return None
    
    @dbg.method_speaker('Empty method! For internal use only!')
    def grid_inner_widgets(self):
        return None
    
    def grid(self, column=None, row=None, sticky=None):
        return None

    def mainloop(self):
        return None

    def start_widget(self):
        self.build_widgets()
        self.grid_inner_widgets()
        self.widget_flag = True
    
    def start_widget_solo(self):
        if not self.widget_flag:
            self.start_widget()
        self.grid(column=0, row=0, sticky='nswe')
        self.tk_parent.update()
        self.tk_parent.minsize(
            self.tk_parent.winfo_width(),
            self.tk_parent.winfo_height()
        )
        self.tk_parent.maxsize(
            self.tk_parent.winfo_width(),
            self.tk_parent.winfo_height()
        )
        self.mainloop()


class CustomTextWidgetRu(ttk.Frame, CommonInterface):
    def __init__(self,
                 parent,
                 label=None,
                 t_width=70,
                 t_height=5,
                 scrol_x=False,
                 btn_clean_all=True,
                 **kwargs):
        ttk.Frame.__init__(self, parent, **kwargs)
        CommonInterface.__init__(self, parent)
        self.label = None
        self.txt = None
        self.scrol_y = None
        self.scrol_x = None
        self.btn_clean_all = None
        self.label_text = label
        self.t_width = t_width
        self.t_height = t_height
        self.scrol_x_flag = scrol_x
        self.btn_flag = btn_clean_all
    
    @dbg.method_speaker('Insertion through keyboard!')
    def custom_insert(self, event): #'<Control-igrave>'
        try:
            self.txt.delete('sel.first', 'sel.last')
        except:
            pass
        try:
            text =  self.selection_get(selection="CLIPBOARD")
        except:
            text = ''
        self.txt.insert(
            index=tk.INSERT,
            chars=text
        )
    
    @dbg.method_speaker('Selection through keyboard!')
    def custom_selection(self, event): #'<Control-ocircumflex>'
        self.txt.tag_add(tk.SEL, '1.0', 'end')
    
    @dbg.method_speaker('Copy through keyboard!')
    def custom_copy(self, event): #'<Control-ntilde>'
        '''
        https://stackoverflow.com/questions/579687/how-do-i-copy-a-string-to-the-clipboard-on-windows-using-python
        '''
        try:
            text = self.txt.get('sel.first', 'sel.last')
        except:
            return 'Fail'
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()
    
    @dbg.method_speaker('Copy and delete through keyboard!')
    def custom_copy_and_delete(self, event): #'<Control-division>'
        res = self.custom_copy(None)
        if not res == 'Fail':
            self.cmd_clean_all()
    
    def custom_binding(self):
        self.txt.bind(
                '<Control-igrave>',
                self.custom_insert
            )
        self.txt.bind(
                '<Control-ocircumflex>',
                self.custom_selection
            )
        self.txt.bind(
                '<Control-ntilde>',
                self.custom_copy
            )
        self.txt.bind(
                '<Control-division>',
                self.custom_copy_and_delete
            )
    
    #@dbg.method_speaker('Clean widget!')
    def cmd_clean_all(self):
        self.txt.delete('1.0', 'end')
    
    #@dbg.method_speaker('Inner insert!')
    def inner_insert(self, start, text):
        self.txt.insert(
            index=start,
            chars=text
        )
    
    #@dbg.method_speaker('Inner get!')
    def inner_get(self, start, stop):
        return self.txt.get(start, stop)

    def build_widgets(self):
        self.label = ttk.Label(self, text=self.label_text)
        self.txt = tk.Text(self, width=self.t_width, height=self.t_height)
        self.scrol_y = ttk.Scrollbar(
            self,
            orient='vertical',
            command=self.txt.yview
        )
        self.scrol_x = ttk.Scrollbar(
            self,
            orient='horizontal',
            command=self.txt.xview
        )
        self.txt['yscrollcommand'] = self.scrol_y.set
        self.txt['xscrollcommand'] = self.scrol_x.set
        self.btn_clean_all = ttk.Button(
            self,
            text='X',
            command=self.cmd_clean_all,
            width=2
        )
        self.custom_binding()
    
    def grid_inner_widgets(self):
        if self.label_text:
            self.label.grid(column=0, row=0, sticky='we')
        self.txt.grid(column=0, row=1, sticky='nw')
        self.scrol_y.grid(column=1, row=1, sticky='nws')
        if self.scrol_x_flag:
            self.scrol_x.grid(column=0, row=2, sticky='wne')
        if self.btn_flag:
            self.btn_clean_all.grid(column=0, row=3, sticky='nw')


if __name__ == '__main__':
    mode = sys.argv[1]
    root = tk.Tk()
    if mode == '-twb':
        ctwr = CustomTextWidgetRu(
            root, label='For example with scrol_x', scrol_x=True
        )
        ctwr.start_widget_solo()
    elif mode == '-twc':
        ctwr = CustomTextWidgetRu(root, label='For example without scrol_x')
        ctwr.start_widget_solo()
    else:
        raise ValueError('Inccorect command line argument!')      
