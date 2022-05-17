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


import sys,json,subprocess
import os
import threading


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


    

class MovieFrame:
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ "
    def __init__(self,root=None,file_path="/Volumes/Movie/Manager",flag="AZ"):
        if root==None:
            self.root=Tk()
        else:
            self.root=root
        start=self.alphabet.find(flag[0])
        end=self.alphabet.find(flag[1])
        self.flag=self.alphabet[start:end+1]
        self.frame = tk.Frame(self.root)
        self.note=ttk.Notebook(self.root,style='lefttab.TNotebook')

        self.all_movie_id=[]
        self.file_path=file_path
        self.update_movies(file_path)
        self.all_movie_info=self.get_movies_info()
        Button(self.root,text="更新列表",command=partial(self.update,file_path)).pack()
        
    def update(self,path):
        tmp=AllMovieInfo(path)
        tmp.gen_file()
        self.all_movie_id=tmp.get_movies()
        self.all_movie_info=self.get_movies_info(force=True)
        self.note.pack_forget()
        self.note=ttk.Notebook(self.root,style='lefttab.TNotebook')
        self.ui()
        
    def update_movies(self,path):
        tmp=AllMovieInfo(path)
        self.all_movie_id.extend(tmp.get_movies())
        
    def parser_movies(self):
        dct={}
        for movie in self.all_movie_id:
            class_,id =movie.split('-')
            if class_ in dct:
                dct[class_].append(movie)
            else:
                dct[class_]=[movie]
        return dct
            
    def get_movies_info(self,force=False):
        file=os.path.join(self.file_path,'classified_movies.json')
        if os.path.exists(file) and force==False:
            with open(file,'r') as f:
                js=json.load(f)
        else:
            js=self.parser_movies()
            with open(file,'w') as f:
                json.dump(js,f)  
        return js 
    
    
    # 生成UI
    def ui(self):
       
            
        def download(id):
            print("Start downloading %s"%id)
            try:
                manage_path=self.file_path
                # path=os.path.join(manage_path,id)
                m=Movie(id)
                mn=MovieName("")
                mn.down_movie(m,manage_path)
            except Exception as e:
                print("Error when downloading %s"%id,e)
                
        def subprocess_download(id):
            trd=threading.Thread(target=download,args=(id,))
            trd.start()
                
        def view(path):
            subprocess.call(["open",path])
            
        def show_image_detail(label,img):
            x,y=img.size
            y=int(y*1.5)
            if y>550:
                k=550/y*1.5
                x=int(x*k)
                y=600
            else:
                x=int(x*1.5)
            img=img.resize((x,y),Image.ANTIALIAS)
            img=ImageTk.PhotoImage(img)
            label.configure(image=img)
            label.image=img

        def show_image_detail_and_copy(label,img,vv):
            show_image_detail(label,img)
            id=deparser_id(vv)
            pyperclip.copy(id)
            
         
        def show_preview(fold,b):
            preview_fold=os.path.join(fold,'preview')
            if os.path.exists(preview_fold):
                v=os.listdir(preview_fold)
                if len(v)>0:
                    for i in range(len(v)):
                        vv=v[i]
                        path=os.path.join(preview_fold,vv)
                        Button(b,text="预览视频",command=partial(view,path)).pack(side=LEFT)
                        
            video_fold=os.path.join(fold,'video')
            if os.path.exists(video_fold):
                v=os.listdir(video_fold)
                if len(v)>0:
                    for i in range(len(v)):
                        vv=v[i]
                        path=os.path.join(video_fold,vv)
                        Button(b,text="完整视频"+vv[:-4],command=partial(view,path)).pack(side=LEFT)
                        
            Button(b,text="打开电影文件夹",command=partial(subprocess.call,['open',fold])).pack(side=LEFT)
                        
                        
        def show_detail(fold,d,det):
            detail_fold=os.path.join(fold,'detail')

            if os.path.exists(detail_fold):
                v=sorted(os.listdir(detail_fold))

                if len(v)>0:
                    for i in range(len(v)):
                        # y=i%4
                        # x=i//4
                        if i%10==0:
                            f=Frame(det)
                            f.pack()
                        vv=v[i]
                        path=os.path.join(detail_fold,vv)
                        tupian=Image.open(path)        
                        tupian2=tupian.resize((160,90),Image.ANTIALIAS)
                        tupian2=ImageTk.PhotoImage(tupian2)
                        # l=Label(f,width=480,height=320)
                        # l.configure(image=tupian2)
                        # l.image=tupian2
                        # l.grid(row=x,column=y) 
                        btn=Button(f,height=72,width=120,command=partial(show_image_detail,d,tupian))
                        btn.configure(image=tupian2)
                        btn.image=tupian2
                        btn.pack(side=LEFT)
                        
        def show_related(fold,lb,det,d):
            related_fold=os.path.join(fold,'related')
            if os.path.exists(related_fold):
                v=os.listdir(related_fold)

                if len(v)>0:
                    for i in range(len(v)):
                        vv=v[i]
                        if i%10==0:
                            r=Frame(det)
                            r.pack()
                        path=os.path.join(related_fold,vv)
                        tupian=Image.open(path)
                        tupian2=tupian.resize((160,90),Image.ANTIALIAS)
                        tupian2=ImageTk.PhotoImage(tupian2)
                        # l=Label(f,width=480,height=320)
                        # l.configure(image=tupian2)
                        # l.image=tupian2
                        # l.grid(row=x,column=y) 
                        rr=Frame(r)
                        rr.pack(side=LEFT)
                        btn=Button(rr,height=72,width=120,command=partial(show_image_detail_and_copy,d,tupian,vv[:-6]))
                        btn.configure(image=tupian2)
                        btn.image=tupian2
                        btn.pack()
                        id=deparser_id(vv[:-6])
                        tmp_name=os.path.join(self.file_path,id)
                        if os.path.exists(tmp_name):
                            btn2=tk.Button(rr,text="查看%s"%id,command=partial(show_info,lb,det,id))
                        else:
                            btn2=tk.Button(rr, text="下载%s"%id,command=partial(subprocess_download,id))
                        btn2.pack()
                        
            
        # 显示图片按钮以及中央的大图预览
        def show_info(lb,det,id="",scd=None):
            for widget in det.winfo_children():
                widget.pack_forget()

                
            b=Frame(det)
            b.pack()
            index=lb.curselection()
            if id=="":
                id=lb.get(index)
                
            fold=os.path.join(self.file_path,id)
            
            show_preview(fold,b)
            
            # 添加打开文件夹的按钮
            
            
            
            f=Frame(det)
            f.pack()
            
            # 放置中间的Label
            k=Frame(det)
            k.pack()

            d=Label(k)
            d.pack(fill=BOTH)
            
            show_detail(fold,d,det)
            
                        
            # 添加相关预览
            r=Frame(det)
            r.pack()
            
            show_related(fold,lb,det,d)
              
        def get_info(root,k,v):
            fr=tk.Frame(root)
            lb=Listbox(fr,width=30,selectmode='single')
            det=Frame(fr)
            lb.bind('<<ListboxSelect>>',partial(show_info,lb,det,""))
            lb.pack(side=LEFT,fill=Y)
            det.pack(side=LEFT,fill=Y)
            v=sorted(v)
            for vv in v:
                lb.insert(END,vv)
            return fr
        
        
        
        for k,v in sorted(self.all_movie_info.items()):
            flag=k[0]
            if flag in self.flag:
                fr=get_info(self.note,k,v)
                self.note.add(fr,text=k.upper())
                
                
       
        
        self.note.pack(fill=BOTH)
        
    def run(self):
        self.root.mainloop() 
            
if __name__ == '__main__':
    m=MovieFrame()
    m.ui()
    m.run()

