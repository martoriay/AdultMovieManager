from tkinter import *

class App(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)

        parent.title("Cluedo Solver 1.0")

        menubar = Menu(root)
        menubar.add_command(label="File")
        menubar.add_command(label="Quit", command=root.quit())

        root.configure(menu=menubar)

root=Tk()
root.geometry("300x250+300+300")
app=App(root)
root.mainloop()