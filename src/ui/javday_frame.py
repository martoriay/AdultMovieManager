# -*- encoding: utf-8 -*-
'''
@File    :   javday_frame.py
@Time    :   2022/05/22 02:42:00
@Author  :   Martoriay 
@Version :   1.0
@Contact :   martoriay@protonmail.com
@License :   (C)Copyright 2021-2022
@Title   :   Javday frame
'''
from asyncio import subprocess
from functools import partial
import json
from sqlite3 import Row
import sys
import os
import threading
sys.path.append(os.path.abspath('./'))
from engin.javday import Javday
import tkinter
from tkinter import *
from tkinter import ttk
from PIL import Image,ImageTk
from ui.base_frame import BaseFrame


class JavdayFrame(BaseFrame):
    def __init__(self,root=None):
        super().__init__(root)
        self.manager_path=os.path.join(self.manager_path,"Javday")
        self.note=ttk.Notebook(self.root)
        self.note.pack()
        self.exist_movies=os.listdir(self.manager_path)
        
    def get_all_movie(self):
        notefrm = Frame()
        if os.path.exists(self.manager_path):
            movie_list=os.listdir(self.manager_path)
            # print(movie_list)
            x=0
            y=0
            max_x=5
            for movie in movie_list:
                frm = self.generate_movie_card(notefrm,movie)
                if frm ==None: continue
                frm.grid(row=y,column=x)
                x+=1
                if x>=max_x:
                    x=0
                    y+=1
        self.note.add(notefrm,text="本地文件")
            
    def generate_movie_card(self,root,movie):
        if movie.startswith('.') or movie in ['Index','Categories']:
            return None
        path=os.path.join(self.manager_path,movie)
        frm=Frame(root)
        f_list = os.listdir(path)
        imgs=[]
        mp4=[]
        jsons=""
        for f in f_list:
            if f.endswith('.jpg'):
                imgs.append(f)
            elif f.endswith(".mp4"):
                mp4.append(f)
            elif f.endswith(".json"):
                jsons=f
                
        if mp4!=[]:
            for m in mp4:

                fp=os.path.join(path,m)
                Button(frm,text="观看"+m[:-4],command=partial(self.view_file,fp)).pack()
        if imgs!=[]:
            for img in imgs:
                img=os.path.join(path,img)
                tupian = Image.open(img)
                tupian=tupian.resize((300,180),Image.ANTIALIAS)
                tupian = ImageTk.PhotoImage(tupian)
                
                lb=Label(frm,width=300,height=180)
                lb.configure(image=tupian)
                lb.image=tupian
                lb.pack()
        if jsons!="":
            with open(self.join(path,jsons),'r') as f:
                tmp=json.load(f)
            for k,v in tmp:
                Label(frm,text='%s:%s'%(k,v)).pack()
        return frm
    
    def get_index_page(self,frm,page_num):
        
        for w in frm.winfo_children():
            w.pack_forget()
        page_size=25
        start_index=page_num*page_size
        end_index=start_index+page_size
        path=os.path.join(self.manager_path,'Index')
        # print("Path:",path)
        if not os.path.exists(path):
            return
        jpgs=os.listdir(path)
        l=len(jpgs)
        if end_index>l:
            end_index=l
        x=0
        y=0
        width=5

        
        try:
            jpgs=jpgs[start_index:end_index]
        except Exception as e:
            print("No more page:",e)
            return
            
        for jpg in jpgs:
            if jpg.endswith('.jpg'):
                p=os.path.join(path,jpg)
                id=jpg.split(' ')[0]
                title = jpg[len(id)+2:-4]
                f=Frame(frm)
                Label(f,text=title).pack()
                if id in self.exist_movies:
                    tmp_p=os.path.join(self.manager_path,id,'1.mp4')
                    Button(f,text="观看",command=partial(self.view_file,tmp_p)).pack()
                else:
                    Button(f,text="下载电影",command=partial(self.download_movie_by_id,id)).pack()
                img=Image.open(p)
                img=img.resize((300,180),Image.ANTIALIAS)
                img=ImageTk.PhotoImage(img)
                lb=Label(f,width=300,height=180)
                lb.configure(image=img)
                lb.image=img
                lb.pack()
                f.grid(row=x,column=y)
                y+=1
                if y>=width:
                    y=0
                    x+=1
        if page_num<l//page_size:
            Button(frm,text="下一页",command=partial(self.get_index_page,frm,page_num+1)).grid(row=6,column=3)
        if page_num>=1:
            Button(frm,text="上一页",command=partial(self.get_index_page,frm,page_num-1)).grid(row=6,column=1)
        Button(frm,text="刷新首页").grid(row=6,column=2)
        
            
        self.note.add(frm,text="首页")
        
    def download_movie_by_id(self,id):
        j=Javday()
        trd=threading.Thread(target=j.multi_download_movie,args=(id,))
        trd.start()
        

        
    

    def ui(self):
        frm=Frame()
        self.get_index_page(frm,0)
        self.get_all_movie()
        
        
    def run(self):
        self.root.mainloop()
    
        
if __name__ == '__main__':
    j=JavdayFrame()
    j.ui()
    j.run()
    
            
        
        