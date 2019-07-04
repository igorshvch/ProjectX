from atctds_search_civil import debugger as dbg

class BuildingInterface():
    def __init__(self):
        pass
    
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
        self.mainloop()
    
    def start_widget_solo(self):
        self.build_widgets()
        self.grid_inner_widgets()
        self.grid(column=0, row=0, sticky='nswe')
        self.mainloop()

