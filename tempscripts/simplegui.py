import tkinter as tk
from tkinter import ttk

class MyGui(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.mainframe = ttk.Frame(self)
        self.mainframe.grid()