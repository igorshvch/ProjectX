import tkinter as tk
from tkinter import ttk

import random as rd

def generate_tokens_secquence(length=5):
    alph = [chr(i) for i in range(97, 123, 1)]
    holder = []
    while length:
        holder.append(''.join(rd.choices(alph, k=rd.randint(3,7))).capitalize())
        length-=1
    return holder

gts = generate_tokens_secquence

def f():
    def inner_f1(tk_var):
        names = gts(rd.randint(3,12))
        tk_var.set(names)
    def inner_f2(tk_var):
        names = ('Ivan', 'Sophia', 'Yjin', 'Jerry', 'Tom', 'Nicolas', 'Jeremy', 'Gerald', 'Jogan')
        tk_var.set(names)
    root = tk.Tk()
    names = ('Ivan', 'Sophia', 'Yjin', 'Jerry', 'Tom', 'Nicolas', 'Jeremy', 'Gerald', 'Jogan')
    var = tk.StringVar(value=names)
    lb = tk.Listbox(root, listvariable=var, height=6, selectmode='extended')
    scrl = ttk.Scrollbar(root, orient='vertical', command=lb.yview)
    lb['yscrollcommand'] = scrl.set
    bt1 = ttk.Button(root, command= lambda :inner_f1(var), text='Press me!')
    bt2 = ttk.Button(root, command= lambda :inner_f2(var), text='Press me too!!')
    lb.pack(side='left')
    scrl.pack(side='left', fill='y')
    bt1.pack()
    bt2.pack()
    root.mainloop()