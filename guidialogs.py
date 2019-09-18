import tkinter as tk
from tkinter import filedialog as fd
#from tkinter import messagebox as msgb

def find_file_path():
    tk.Tk().withdraw()
    return fd.askopenfilename()

def find_directory_path():
    tk.Tk().withdraw()
    return fd.askdirectory()

def find_file_paths():
    tk.Tk().withdraw()
    return fd.askopenfilenames()

ffp = find_file_path
ffps = find_file_paths
fdp = find_directory_path