import tkinter as tk
from tkinter import filedialog as fd
#from tkinter import messagebox as msgb

def find_file_path():
    tk.Tk().withdraw()
    return fd.askopenfilename()

def find_directory_path():
    tk.Tk().withdraw()
    return fd.askdirectory()

ffp = find_file_path
fdp = find_directory_path