import os
import tkinter as tk
import send2trash as st
from tkinter import messagebox

window = tk.Tk()

window.title("Wallpaper Filter")
window.geometry('260x330')
window.resizable(False, False)
e_1 = tk.Entry(window, show=None, width=35)
b_1 = tk.Button(window,
                text='预处理',
                width=35,
                height=2).pack()

window.mainloop()
