import tkinter as tk
from tkinter import ttk

from .patterns import CommonInterface
from .filemanager import FileManager
from .treeview import TreeView
from .listview import ListView, ListViewTest
from .datebox import DateBox, DateBoxTest
from .textarea import TextArea, TextAreaTest
from .controlbuttons import ControlButtons
from .resarea import ResArea
from .reslist import ResList

from atctds_search_civil import debugger as dbg

class MainFrame(ttk.Frame, CommonInterface):
    def __init__(self, parent, icon_path=None, **kwargs):
        ttk.Frame.__init__(self, parent, **kwargs)
        CommonInterface.__init__(self, parent)
        self.sep_ta = None # ttk.Separator for TextArea widget area
        self.sep_fm = None # ttk.Separator for FileManager widget area
        self.sep_lv = None # ttk.Separator for ListView widget area
        self.sep_cb = None # ttk.Separator for ControlButtons widget area
        self.sep_lp = None # ttk.Separator for left panel
        self.sep_rl = None # ttk.Separator for ResList widget area
        self.icon_path = icon_path
        
    def initiate_main_widgets(self):
        self.widgets = {
            'FileManager': FileManager(self),
            'ListView': ListView(self),
            'DateBox': DateBox(self),
            'TextArea': TextArea(self),
            'ControlButtons': ControlButtons(self),
            'ResList': ResList(self),
            'ResArea': ResArea(self)
        }
        if self.icon_path:
            self.widgets['ListView'].icon_path = self.icon_path
    
    def build_widgets(self):
        self.initiate_main_widgets()
        for widget_name in self.widgets:
            self.widgets[widget_name]['padding'] = (3, 5, 3, 5)
            #self.widgets[widget_name]['relief'] = 'sunken'
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
        self.sep_cb = ttk.Separator(
            self,
            orient='vertical'
        )
        self.sep_lp = ttk.Separator(
            self,
            orient='horizontal'
        )
        self.sep_rl = ttk.Separator(
            self,
            orient='vertical'
        )
    
    def grid_inner_widgets(self):
        self.widgets['FileManager'].grid(
            column=0,
            row=0,
            columnspan=5,
            sticky='nwe'
        )
        #Sep vertical:
        self.sep_ta.grid(
            column=5,
            row=0,
            #rowspan=2,
            sticky='wns'
        )
        self.widgets['TextArea'].grid(
            column=6,
            row=0,
            #rowspan=3,
            sticky='nw'
        )
        #Sep horizontal:
        self.sep_fm.grid(
            column=0,
            row=1,
            columnspan=7,
            sticky='nwe'
        )
        self.widgets['ListView'].grid(
            column=0,
            row=2,
            columnspan=3,
            sticky='nw'
        )
        #Sep horizontal:
        self.sep_lv.grid(
            column=0,
            row=3,
            columnspan=3,
            sticky='nwe'
        )
        self.widgets['DateBox'].grid(
            column=0,
            row=4,
            sticky='wn'
        )
        #Sep vertical:
        self.sep_cb.grid(
            column=1,
            row=4,
            #rowspan=2,
            sticky='wns'
        )
        self.widgets['ControlButtons'].grid(
            column=2,
            row=4,
            sticky='wn'
        )
        #Sep horiaontal:
        self.sep_lp.grid(
            column=0,
            row=5,
            columnspan=3,
            sticky='nwe'
        )
        self.widgets['ResList'].grid(
            column=0,
            row=6,
            columnspan=3,
            sticky='nw'
        )
        #Sep vertical:
        self.sep_rl.grid(
            column=3,
            row=2,
            rowspan=6,
            sticky='wns'
        )
        self.widgets['ResArea'].grid(
            column=4,
            row=2,
            columnspan=3,
            rowspan=6,
            sticky='nwse'
        )
        self.rowconfigure(7, weight=1)
        self.columnconfigure(4, weight=1)

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
            'TextArea': TextAreaTest(self),
            'ControlButtons': ControlButtons(self)
        }
        print(self.widgets['FileManager'].__class__.__name__)
        print(self.widgets['ListView'].__class__.__name__)
        print(self.widgets['DateBox'].__class__.__name__)
        print(self.widgets['TextArea'].__class__.__name__)
        print(self.widgets['ControlButtons'].__class__.__name__)