import tkinter as tk
from tkinter import ttk

from .patterns import CommonInterface
from .filemanager import FileManager
from .treeview import TreeView
from .listview import ListView, ListViewTest
from .datebox import DateBox, DateBoxTest
from .textarea import TextArea

from atctds_search_civil import debugger as dbg

class MainFrame(ttk.Frame, CommonInterface):
    def __init__(self, parent, **kwargs):
        ttk.Frame.__init__(self, parent, **kwargs)
        CommonInterface.__init__(self, parent)
        self.sep_fm = None # ttk.Separator for FileManager widget area
        self.sep_lv = None # ttk.Separator for ListView widget area
        self.sep_ta = None # ttk.Separator for TextArea widget area
        
    def initiate_main_widgets(self):    
        self.widgets = {
            'FileManager': FileManager(self),
            'ListView': ListView(self),
            'DateBox': DateBox(self),
            'TextArea': TextArea(self)
        }
    
    def build_widgets(self):
        self.initiate_main_widgets()
        for widget_name in self.widgets:
            self.widgets[widget_name]['padding'] = (3, 5, 3, 5)
            self.widgets[widget_name].start_widget()
        self.sep_fm = ttk.Separator(
            self,
            orient='horizontal'
        )
        self.sep_lv = ttk.Separator(
            self,
            orient='horizontal'
        )
        self.sep_ta = ttk.Separator(
            self,
            orient='vertical'
        )
    
    def grid_inner_widgets(self):
        self.widgets['FileManager'].grid(
            column=0,
            row=0,
            columnspan=3,
            sticky='we'
        )
        #Sep horizontal:
        self.sep_fm.grid(
            column=0,
            row=1,
            columnspan=3,
            sticky='we'
        )
        self.widgets['ListView'].grid(
            column=0,
            row=2,
            sticky='w'
        )
        #Sep vertical:
        self.sep_ta.grid(
            column=1,
            row=2,
            rowspan=3,
            sticky='wns'
        )
        self.widgets['TextArea'].grid(
            column=2,
            row=2,
            rowspan=3,
            sticky='nw'
        )
        #Sep horizontal:
        self.sep_lv.grid(
            column=0,
            row=3,
            sticky='we'
        )
        self.widgets['DateBox'].grid(
            column=0,
            row=4,
            sticky='w'
        )

###############################################################################
############################### testing: ######################################
###############################################################################

class MainFrameTest(MainFrame):
    def __init__(self, parent, **kwargs):
        MainFrame.__init__(self, parent, **kwargs)
    
    def initiate_main_widgets(self):    
        self.widgets = {
            'FileManager': FileManager(self),
            'ListView': ListViewTest(self),
            'DateBox': DateBoxTest(self),
            'TextArea': TextArea(self)
        }
        print(self.widgets['FileManager'].__class__.__name__)
        print(self.widgets['ListView'].__class__.__name__)
        print(self.widgets['DateBox'].__class__.__name__)
        print(self.widgets['TextArea'].__class__.__name__)
