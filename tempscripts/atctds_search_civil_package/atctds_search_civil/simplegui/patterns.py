from atctds_search_civil import debugger as dbg

class CommonInterface():
    def __init__(self, tk_parent):
        self.tk_parent = tk_parent
    
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
    
    def start_widget_solo(self):
        self.start_widget()
        self.grid(column=0, row=0, sticky='nswe')
        self.tk_parent.update()
        self.tk_parent.minsize(
            self.tk_parent.winfo_width(),
            self.tk_parent.winfo_height()
        )
        self.mainloop()

