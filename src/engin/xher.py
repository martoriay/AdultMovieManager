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

class Xher(Engin):
    def __init__(self):
        self.engin_path='/Volume/Movie/'
        super().__init__('https://xher.net/')
        # self.headers['X-Playback-Session-Id']="7D7C298F-9D13-412A-9550-37D513483C8E"
        self.engin_path = os.path.join(self.manager_path,'Xher')
        if not os.path.exists(self.engin_path):
            os.mkdir(self.engin_path)
        self.database_file=os.path.join(self.engin_path,'xher.db')
        if not os.path.exists(self.database_file):
            self.create_db()
            print("Database xher.db created.")
        
    def create_db(self):
        con=connect(self.database_file)
        con.close()
 
    def create_tb(self,name):
        check_sql="SELECT count(*) FROM sqlite_master WHERE type='table' AND name='%s'"%name
        con=connect(self.database_file)
        cur=con.cursor()
        # res=cur.execute(check_sql)
        # if res!=0:
        #     con.close()
        #     return 

        sql="""
        CREATE TABLE %s (
            id text primary key, 
            title text, 
            pic text,
            total integer,
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
        a=pic.select('a')[0]
        id=a.get('href')
        img=pic.select('img')[0]
        title=img.get('alt')
        if "'" in title:
            title2=""
            for c in title:
                if c !="'":
                    title2+=c 
            title=title2
        ppic=img.get('src')
        total_soup=pic.select('div')[-1].get_text()
        total=int(total_soup.split(' ')[0])
        
        dct={
            'id':id,
            'title':title,
            'pic':ppic,
            'total':total,
            'saved':0
        }
        return dct
    
    def exist_or_insert_single(self,dct,cur,table='xher'):
        sql="INSERT or IGNORE into %s values ( '%s','%s','%s',%d,%d);"%(table,dct['id'],dct['title'],dct['pic'],dct['total'],dct['saved'])
        try:
            cur.execute(sql)
            print(dct['id']," have been inserted to table")
        except Exception as e:
            print("Error when insert %s:"%dct[id],e)
        
        
    def exist_or_insert_multi(self,dcts,table='cosplay'):
        values=""
        con=connect(self.database_file)
        cur=con.cursor()
        for i in range(len(dcts)):
            dct=dcts[i]
            self.exist_or_insert_single(dct,cur,table)
        con.commit()
        con.close()
      
    def get_page_pic_list(self,url):
        soup=self.get_soup(url)
        lst=self.get_content_from_soup(soup,'.content>ul>li')
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

    def insert_all_pages(self,table,first_page_url):
        # self.create_tb(table)
        count=1
        print("####### Start insert page %d to Database########"%count)
        
        self.insert_page_list_into_database(first_page_url,table)
        
        next_url=first_page_url
        while True:
            count+=1
            soup=self.get_soup(next_url)
            next_soup=soup.select('span.navPrevNext')[1].select('a')
            if next_soup==[]:
                break
            else:
                next_url=self.base_url+next_soup[0].get('href')
            print("####### Start insert page %d to Database########"%count)
            self.insert_page_list_into_database(next_url,table)
            
        print("All pages have been inserted into the Database.")
        
    # 从数据库中下载所有封面图，并建立文件夹  
    def create_fold_and_download_pic(self,r,table):
        id=r[0]
        url=self.base_url+id
        
        tmp=id.split('/')

        iid=tmp[-1]
        pic_path=os.path.join(self.engin_path,iid)
        if not os.path.exists(pic_path):
            os.mkdir(pic_path)
        title=r[1]
        pic=r[2]
        pic_url=self.base_url+pic
        total=r[3]
        saved=r[4]
        
        self.download_single(pic_url,pic_path,'post.jpg')
        
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
        def get_large(detail_url):
            soup=self.get_soup(detail_url)
            img=soup.select('img')[0]
            pic_url=self.base_url+img.get('src')
            return pic_url

        def get_pic_in_page(url):
            soup=self.get_soup(url)
            pages_soup=soup.select('#thumbnails>li>a')
            for a in pages_soup:
                tmp=a.get('href')
                detail_url=self.base_url+tmp
                pic_url=get_large(detail_url)
                #all_pics.append(pic_url)
                title=pic_url.split('/')[-1]
                self.download_single(pic_url,path,title)
            next_soup=soup.select('span.navPrevNext')[1].select('a')
            return next_soup
        
        next_url=url
        count=1
        while True:
            print("####### Start insert page %d to all pics########"%count)
            next_soup=get_pic_in_page(next_url)
            try:
                if next_soup==[]:
                    break
                else:
                    next_url=self.base_url+next_soup[0].get('href')
                count+=1
            except Exception as e:
                print("Error:",e)
                break
        
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
    x=Xher()
    x.get_all_pics_from_database('xher')