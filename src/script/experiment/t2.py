import tkinter as tk
 
app = tk.Tk() 
app.geometry('300x200')
app.title("Basic Menu Bar")

menubar = tk.Menu(app)

filemenu = tk.Menu(menubar)
filemenu.add_command(label="Open")
filemenu.add_command(label="Save")
filemenu.add_command(label="Exit")

menubar.add_cascade(label="File", menu=filemenu)

app.config(menu=menubar)

app.mainloop()