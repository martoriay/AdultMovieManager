# -*- encoding: utf-8 -*-
'''
@File    :   javday.py
@Time    :   2022/05/21 05:01:32
@Author  :   Martoriay 
@Version :   1.0
@Contact :   martoriay@protonmail.com
@License :   (C)Copyright 2021-2022
@Title   :   
'''


from concurrent.futures import thread
import json
from posixpath import split
import sys
import os
from tkinter.ttk import Notebook
from unicodedata import category
import pyperclip
sys.path.append(os.path.abspath('./'))
import requests
import time
from bs4 import BeautifulSoup as bs 
import threading
from threading import Lock
from engin.base import Engin
import tkinter as tk 
from tkinter import *
from tkinter import messagebox
from functools import partial
import sqlite3
from sqlite3 import connect

class W169(Engin):
    def __init__(self):
        super().__init__('https://www.169w.cc/')
        # self.headers['X-Playback-Session-Id']="7D7C298F-9D13-412A-9550-37D513483C8E"
        self.engin_path = os.path.join(self.manager_path,'W169')
        if not os.path.exists(self.engin_path):
            os.mkdir(self.engin_path)
        self.database_file=os.path.join(self.engin_path,'w169.db')
        if not os.path.exists(self.database_file):
            self.create_db()
            print("Database w169.db created.")
            self.create_tb('w169')
            print("table w169 created.")
        
    def create_db(self):
        con=connect(self.database_file)
        con.close()
 
    def create_tb(self,name):
        con=connect(self.database_file)
        cur=con.cursor()

        sql="""
        CREATE TABLE %s (
            id text primary key, 
            title text, 
            pic text,
            saved integer);
        """%name
        cur.execute(sql)
        con.commit()
        con.close()
        print("Table cosplay created.")
        
            
    def single_execute(self,sql):
        con=sqlite3.connect(self.database_file)
        cur=con.cursor()
        res = cur.execute(sql)
        con.commit()
        con.close()
        return res
        
        
    def from_single_soup_to_dict(self,pic):
        id=pic.get('href')
        img=pic.select('img')[0]
        img_url=img.get('src')
        title=img.get('alt')
        if "'" in title:
            title2=""
            for c in title:
                if c !="'":
                    title2+=c 
            title=title2
        
        dct={
            'id':id,
            'title':title,
            'pic':img_url,
            'saved':0
        }
        return dct
    
    def exist_or_insert_single(self,dct,cur,table='w169'):
        sql="INSERT or IGNORE into %s values ( '%s','%s','%s',%d);"%(table,dct['id'],dct['title'],dct['pic'],dct['saved'])
        try:
            cur.execute(sql)
            print(dct['id']," have been inserted to table")
        except Exception as e:
            print("Error when insert %s:"%dct[id],e)
        
        
    def exist_or_insert_multi(self,dcts,table='w169'):
        con=connect(self.database_file)
        cur=con.cursor()
        for i in range(len(dcts)):
            dct=dcts[i]
            self.exist_or_insert_single(dct,cur,table)
        con.commit()
        con.close()
      
    def get_page_pic_list(self,url):
        soup=self.get_soup(url)
        lst=self.get_content_from_soup(soup,'#dlNews>tr>td>a')
        return lst
    
    def get_dcts_from_lst(self,lst):
        dcts=[]
        for pic in lst:
            dct=self.from_single_soup_to_dict(pic)
            dcts.append(dct)
        return dcts 
    
    def insert_page_list_into_database(self,url,table):
        lst=self.get_page_pic_list(url)
        dcts=self.get_dcts_from_lst(lst)
        self.exist_or_insert_multi(dcts,table)

    def insert_all_pages(self,table,start=1):
        for i in range(start,72):
            next_url=self.base_url+'c49p'+str(i)+'.aspx'
            print("####### Start insert page %d to Database########"%i)
            self.insert_page_list_into_database(next_url,table)
        print("All pages have been inserted into the Database.")

    # def ui(self,root=None,single=True):
    #     if root==None:
    #         root=tk.Tk()
    #         root.geometry('800x480')
    #     note=Notebook(root)
    #     frm_game=Frame(note)
    #     note.add(frm_game,text="Game")
    #     frm_china=Frame(note)
    #     note.add(frm_china,text="China")
    #     frm_japan=Frame(note)
    #     note.add(frm_japan,text="Japan")
    #     frm_hot=Frame(note)
    #     note.add(frm_hot,text="Hot")

        # note.pack()
        # if single:
        #     root.mainloop()
        # else:
        #     return note
        
    # 从数据库中下载所有封面图，并建立文件夹
    
    def create_fold_and_download_pic(self,r,table):
        id=r[0]
        url=self.base_url+id
        tmp=id.split('.')
        iid=tmp[0]
        
        pic_path=os.path.join(self.engin_path,iid)
        if not os.path.exists(pic_path):
            os.mkdir(pic_path)
        
        title=r[1]
        pic=r[2]
        pic_url=self.base_url+pic
        saved=r[3]
        
        self.download_single(pic_url,pic_path,'%s.jpg'%title)
        
        self.get_detail_pic(url,pic_path)
        saved+=1
        sql="UPDATE %s SET saved='%d' WHERE id='%s'"%(table,saved,id)
        
        def update_database():
            try:
                con=sqlite3.connect(self.database_file)
                cur=con.cursor()
                cur.execute(sql)
                print("%s database UPDATED"%id)
                con.commit()
                con.close()
            except Exception as e:
                print("Error: ",e)
                time.sleep(2)
                update_database()
        update_database()
        
    def get_detail_pic(self,url,path):
        
        def get_pic_from_soup(soup):
            imgs=soup.select('#content>div>div>img')
            res=[]
            for i in imgs:
                res.append(self.base_url+i.get('src'))
            return res
        
        soup=self.get_soup(url)
        pages=soup.select('.pager>ul>li>a')
        pages_url=[]
        for p in pages:
            a=p.get('href')
            pages_url.append(self.base_url+a)
        pages_url=pages_url[:-1]
        
        pics=get_pic_from_soup(soup)
        
        for p in pages_url:
            soup=self.get_soup(p)
            pics.extend(get_pic_from_soup(soup))
        
        count=1
        for pic in pics:
            title=str(count)+'.jpg'
            self.download_single(pic,path,title)
            count+=1
            
    def get_all_pics_from_database(self,table):
        sql="select * from %s where saved=0"%table
        con=sqlite3.connect(self.database_file)
        cur=con.cursor()
        res=cur.execute(sql)
        records=[]
        for r in res:
            records.append(r)
        con.commit()
        con.close()
        for r in records:
            self.create_fold_and_download_pic(r,table)
        return True

if __name__ == '__main__':
    x=W169()
    x.get_all_pics_from_database('w169')