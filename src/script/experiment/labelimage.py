from tkinter import *
import tkinter as tk 
from PIL import Image, ImageTk

root=Tk()

tupian=Image.open("/Volumes/Movie/Manager/IPX-707/detail/ipx00707jp-1.jpg")
tupian2=ImageTk.PhotoImage(tupian)
for i in range(2):
    Label(root,image=tupian2).pack()
root.mainloop()


