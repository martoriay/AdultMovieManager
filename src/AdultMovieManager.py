# -*- encoding: utf-8 -*-
'''
@File    :   window.py
@Time    :   2022/05/12 13:45:24
@Author  :   Muyao ZHONG 
@Version :   1.0
@Contact :   zmy125616515@hotmail.com
@License :   (C)Copyright 2019-2020
@Title   :   baseUI
'''

import threading
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import sys,os,json
from functools import partial
import pyperclip



sys.path.append(os.path.abspath('./'))
print(os.path.abspath('./'))
from utils.config import get_config,set_config
from utils.search import Search
from utils.movie import Movie
from ui.manager_frame import MovieFrame
from utils.movie_parser import MovieName
from ui.category_frame import CategoryFrame


class MainUI:
    app=tk.Tk()
    app.geometry("1920x1550")
    app.title("Adult Movie Manager")
    data={
        "config_path":"base_config.json"
    }
    result_frame=None
    to_be_download=[]
    
    def __init__(self):
        
        # self.config_data=get_config(self.data['config_path'])
        
        self.set_config=partial(set_config,self.data["config_path"])
        self.get_config=partial(get_config,self.data["config_path"])
        
        self.site_url=tk.StringVar(value=self.get_config("site_url"))
        self.file_path=tk.StringVar(value=self.get_config("file_path"))
        self.manager_path=tk.StringVar(value=self.get_config("manager_path"))
        self.engin=Search(self.site_url.get())
        self.menu_bar()
        self.note_book()
        
    def search(self,keyword):
        res=self.engin.search(keyword)
        return res
        
    
    def run(self):
        self.app.mainloop()
        
    ####### 菜单栏
    def about(self):
        top1=tk.Toplevel() 
        # top1.geometry("480x320")
        Label(top1,text="版本号：0.0.1").pack()
        Label(top1,text="开发者：Mythezone").pack()
        Label(top1,text="邮箱：mythezone@mythezone.net").pack()
        
    def exit(self):
        sys.exit()
        
    def config(self):
        cfg=tk.Toplevel()
        Label(cfg,text="BTSOW站点：").grid(row=0,column=0)
        site_url_entry=Entry(cfg,textvariable=self.site_url)
        site_url_entry.grid(row=0,column=1)
        
        Label(cfg,text="文件路径：").grid(row=1,column=0)
        file_path_entry=Entry(cfg,textvariable=self.file_path)
        file_path_entry.grid(row=1,column=1)
        
        Label(cfg,text="电影管理目录：").grid(row=2,column=0)
        manager_path_entry=Entry(cfg,textvariable=self.manager_path)
        manager_path_entry.grid(row=2,column=1)
        

        def submit_config():
            dct={
                "site_url": site_url_entry.get(),
                "file_path":file_path_entry.get(),
                "manager_path":manager_path_entry.get()
            }
            
            self.set_config(dct)
            try:
                self.engin=Search(dct["site_url"])
            except:
                print("Illegel Search Engin")
            cfg.destroy()
        
        def cancle():
            cfg.destroy()
            
        Button(cfg,text="取消",command=cancle).grid(row=4,column=0)
        Button(cfg,text="保存",command=submit_config).grid(row=4,column=1)
        
    def menu_bar(self):
        menubar = tk.Menu(self.app)
        filemenu = tk.Menu(menubar)
        filemenu.add_command(label="关于",command=self.about)
        filemenu.add_command(label="软件设置",command=self.config)
        
        filemenu.add_command(label="退出",command=self.exit)
        
        menubar.add_cascade(label="文件",menu=filemenu)
        self.app.config(menu=menubar)
        
    ### 标签页功能
    
    ##### 首页
    def note_book(self):
        notebook=ttk.Notebook(self.app)
        homePage=tk.Frame()
        self.home_page(homePage)
        
        cate_page=tk.Frame()
        self.category_page(cate_page)
        
        download_list=tk.Frame(height=800)
        self.download_list(download_list)
        managePage=tk.Frame()
        self.manage_page(managePage,"AF")
        managePage2=tk.Frame()
        self.manage_page(managePage2,"GM")
        managePage3=tk.Frame()
        self.manage_page(managePage3,"NZ")
        download_movie_detail=tk.Frame()
        self.download_movie(download_movie_detail)
        
        notebook.add(cate_page,text="分类浏览")
        notebook.add(homePage,text="首页")
        notebook.add(download_list,text="下载列表")
        notebook.add(download_movie_detail,text="下载详情")
        notebook.add(managePage,text="电影A-F")
        notebook.add(managePage2,text="电影G-M")
        notebook.add(managePage3,text="电影N-Z")
        notebook.pack(fill=tk.BOTH,expand=True)
        
    def manage_page(self,frame,flag):
        path=self.get_config('manager_path')
        m=MovieFrame(frame,path,flag)
        m.ui()
        return m.frame
    
    def category_page(self,frame):
        c=CategoryFrame(frame)
        return c.frame
    
    def download_movie(self,frame):
        def download(ety):
            inp=ety.get()
            print("Start downloading %s"%inp)
            if inp == "":
                return
            res=inp.split(' ')
            res=[i.strip() for i in res]
            for id in res:
                id=id.upper()
                try:
                    manage_path=self.get_config('manager_path')
                    # path=os.path.join(manage_path,id)
                    m=Movie(id)
                    mn=MovieName("")
                    mn.down_movie(m,manage_path)
                except Exception as e:
                    print("Error when downloading %s"%id,e)
            search=res[0].upper()
            self.search_key_entry.delete(0,END)
            self.search_key_entry.insert(0,search) 
            
        def subprocess_download(ety):
            trd=threading.Thread(target=download,args=(ety,))
            trd.start()

        Label(frame,text="输入你想要下载的电影ID，多个电影请用空格隔开：").pack()
        ety=Entry(frame,textvariable=StringVar())
        ety.pack()
        Button(frame,text="开始下载",command=partial(subprocess_download,ety)).pack()
        
    def home_page(self,frame):
        Label(frame,text="关键字：").pack()
        key_words=tk.StringVar(value="")
        key_entry=Entry(frame,textvariable=key_words)
        self.search_key_entry=key_entry
        key_entry.pack()

        def add_download(movie):
            self.to_be_download.append(movie)
            self.download_lb.insert(END,movie.title)
        
        def search():
            kw=key_entry.get()
            print("get keyword:",key_words.get())
            if self.result_frame !=  None:
                self.result_frame.pack_forget()
            self.result_frame=Frame(frame)
            res=self.search(kw)
            if res == []:
                return
            for i in range(len(res)):
                r=res[i]
                Label(self.result_frame,text=r.title,justify=LEFT).grid(row=i,column=0)
                Label(self.result_frame,text=r.info,justify=LEFT).grid(row=i,column=1)
                Button(self.result_frame,text="复制Hash",command=partial(pyperclip.copy,r.hash)).grid(row=i,column=2)
                Button(self.result_frame,text="添加到待下载列表",command=partial(add_download,r)).grid(row=i,column=3)
            self.result_frame.pack()
        
        Button(frame,text="搜索",command=search).pack()
        
    def download_list(self,frame):
        Label(frame,text="待下载电影").pack()
        self.download_lb=Listbox(frame,selectmode=EXTENDED)
        
        self.download_lb.select_set(0)
        # lb_info=Label(frame,text="title:\ninfo:\nhash:\n")
        # lb_info.pack()
        self.all_info=None
        
        def get_all_hash():
            pass
        
        def clear_list():
            self.to_be_download=[]
            
        def get_info():
            if self.all_info != None:
                self.all_info.pack_forget()
            self.all_info=Frame(frame)

            index=self.download_lb.curselection()
            for i in index:
                movie=self.to_be_download[i]
                Label(self.all_info,text="标题:%s\n信息:%s\nHASH:%s\n"%(movie.title,movie.info,movie.hash)).pack()
            self.all_info.pack()
            
        def delete_movie_from_list():
            index=self.download_lb.curselection()
            self.download_lb.delete(index)
            self.to_be_download=[self.to_be_download[i] for i in range(len(self.to_be_download)) if i not in index]
            
        def get_all_hash():
            res=""
            for m in self.to_be_download:
                res+=m.hash+"\n"
            pyperclip.copy(res)
            messagebox.showinfo("提示","所选电影的HASH已经拷贝到剪切板")
        
        def clear_list():
            
            self.download_lb.delete(0,len(self.to_be_download))
            self.to_be_download=[]
            
        Button(frame,text="获取选择电影的信息",command=get_info).pack()
        Button(frame,text="删除所选电影",command=delete_movie_from_list).pack()
        Button(frame,text="复制所有Hash",command=get_all_hash).pack()
        Button(frame,text="清空列表",command=clear_list).pack()
        self.download_lb.pack(fill=BOTH)
        


if __name__ == "__main__":
    mui=MainUI()
    mui.run()