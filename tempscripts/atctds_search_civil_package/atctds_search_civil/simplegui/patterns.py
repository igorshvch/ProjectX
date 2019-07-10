from atctds_search_civil import debugger as dbg

class CommonInterface():
    def __init__(self, tk_parent):
        self.tk_parent = tk_parent
        self.widget_dict = {}
        self.widget_flag = False
    
    def retrieve(self, key):
        '''
        Internal acting function providing interface to access
        inner widgets of particluar tk.Frame subclass
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
        self.mainloop()

