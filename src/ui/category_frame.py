# -*- encoding: utf-8 -*-
'''
@File    :   manager_frame.py
@Time    :   2022/05/13 10:53:27
@Author  :   Muyao ZHONG 
@Version :   1.0
@Contact :   zmy125616515@hotmail.com
@License :   (C)Copyright 2019-2020
@Title   :   File Manager
'''



from sre_constants import ANY_ALL
import sys,json,subprocess
import os
import threading
from matplotlib.pyplot import show


import pyperclip
sys.path.append(os.path.abspath('./'))

import tkinter as tk 

from tkinter import *
from tkinter import ttk
from PIL import Image,ImageTk
from utils.movie import Movie,AllMovieInfo

from functools import partial

from utils.common import deparser_id
from utils.movie_parser import MovieName

from utils.category_manager import CategoryManager,Category


class CategoryFrame:
    file_path = "/Volumes/Movie/Manager/Categories"
    
    def __init__(self,root=None):
        if root == None:
            self.root = Tk()
        else:
            self.root = root
            
        self.frame=tk.Frame(self.root)
            
        self.cm=CategoryManager()
        self.cm.load_categories_info()
        self.keys=self.cm.categories.keys()
        
        self.note=ttk.Notebook(self.root,width=1920,height=1080,style='lefttab.TNotebook')
        
        for title,categories in self.cm.categories.items():
            fr = self.gen_note(self.note,title,categories)
            self.note.add(fr,text=title)
            
        self.note.pack(fill=BOTH)

        
    def gen_note(self,root,title,categories):
        
        def show_detail_image(img):
            top=Toplevel(width=800,height=538)
            l=Label(top)
            size=img.size
            
            img=img.resize((size[0]*2,size[1]*2),Image.ANTIALIAS)
            img=ImageTk.PhotoImage(img)
            l.configure(image=img)
            l.image=img
            l.pack()
        
        def show_info(lb,det,title="",page_num=0,scd=None):
            for widget in det.winfo_children():
                widget.pack_forget()
            
            index=lb.curselection()
            if title=="":
                title=lb.get(index)
            
            movies_path = os.path.join(self.file_path,title)
        
            
            if os.path.exists(movies_path):
                movies_path=os.path.join(movies_path,"full")
                movies=os.listdir(movies_path)
                
                total = len(movies)
                length=5
                count=0
                page=25
                max_page=int(total//page)
                for movie in movies[page_num*page:(page_num+1)*page]:
                    # print(movie)
                    if movie.endswith(".jpg"):
                        x=int(count//length)
                        y=int(count%length)
                        count+=1
                        movie_file = os.path.join(movies_path,movie)
                        tmp_fr=Frame(det,padx=5,pady=10)
                        tmp_fr.grid(row=x,column=y)
                        tupian=Image.open(movie_file)
                        size=tupian.size
                        tupian2=tupian.resize((300,150),Image.ANTIALIAS)
                        tupian2=ImageTk.PhotoImage(tupian)

                        btn1=Button(tmp_fr,height=150,width=300,command=partial(show_detail_image,tupian))
                        btn1.configure(image=tupian2)
                        btn1.image=tupian2
                        btn2=Button(tmp_fr,text="下载内容",command=partial(print,"hello,world"))
                        btn1.pack()
                        btn2.pack()
                if page_num>1:
                    Button(det,text="上一页",command=partial(show_info,lb,det,"",page_num-1)).grid(row=5,column=1)
                if page_num<max_page-1:
                    Button(det,text="下一页",command=partial(show_info,lb,det,"",page_num+1)).grid(row=5,column=3)
            
            
        
        fr = Frame(root)
        lb=Listbox(fr,width=30,selectmode='single')
        det=Frame(fr)
        lb.bind('<<ListboxSelect>>',partial(show_info,lb,det,"",0))
        lb.pack(side=LEFT,fill=Y)
        det.pack(side=LEFT,fill=Y)
        categories=sorted(categories,key=lambda x:x['title'])
        for cate in categories:
            lb.insert(END,cate['title'])
        return fr
    

    
    def run(self):
        self.root.mainloop()
    
    
if __name__ == '__main__':
    c=CategoryFrame()
    c.run()
    
    
        
        
        
        
        
        

