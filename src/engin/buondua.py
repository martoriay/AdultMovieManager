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


from concurrent.futures import ThreadPoolExecutor, thread
import json
from posixpath import split
import sys

import os
from tkinter.ttk import Notebook
from unicodedata import category
from matplotlib import collections
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

class Buodua(Engin):
    def __init__(self):
        super().__init__('https://buondua.com',"Buondua")
        self.database_file=os.path.join(self.engin_path,'%s.db'%self.engin_name)
        if not os.path.exists(self.database_file):
            self.create_db()
            print("Database buondua.db created.")
            self.create_tb('cosplayer')
        try:
            self.create_collection_tb()
        except:
            print("Table exist.")
            
        try:
            self.create_pic_tb()
        except:
            print("Table exist.")
            
    def create_db(self):
        con=connect(self.database_file)
        con.close()
 
    def create_tb(self,name):
        check_sql="SELECT count(*) FROM sqlite_master WHERE type='table' AND name='%s'"%name
        con=connect(self.database_file)
        cur=con.cursor()

        sql="""
        CREATE TABLE %s (
            id text primary key,
            info integer,
            saved integer);
        """%name
        cur.execute(sql)
        con.commit()
        con.close()
        print("Table cosplay created.")
        
    def create_collection_tb(self):
        con=connect(self.database_file)
        cur=con.cursor()
        sql="""
        CREATE TABLE collection (
            title text primary key,
            herf text,
            post text,
            saved integer);
        """
        cur.execute(sql)
        con.commit()
        con.close()
        print("Table cosplay created.")
        
    def create_pic_tb(self):
        con=connect(self.database_file)
        cur=con.cursor()
        sql="""
        CREATE TABLE pics (
            url text primary key,
            path text,
            name text,
            saved integer);
        """
        cur.execute(sql)
        con.commit()
        con.close()
        print("Table pics url created.")
        
    def get_soup(self,url,debug=False):
        html=requests.get(url,headers=self.headers)
        if debug:
            print("Response:",html.status_code)
        html.encoding = 'utf-8'
        soup = bs(html.text,features="html.parser")
        return soup
        
    def update_cosplayers_db(self,dcts):
        con=connect(self.database_file)
        cur=con.cursor()
        for dct in dcts:
            sql="INSERT or IGNORE into cosplayer values ('%s',%d,%d);"%(dct['id'],dct['info'],dct['saved'])
            cur.execute(sql)
        con.commit()
        con.close()
        
    def update_cosplayer_collections(self,id):
        con=connect(self.database_file)
        cur=con.cursor()
        sql="UPDATE cosplayer SET info=1 WHERE id='%s'"%(id)
        cur.execute(sql)
        con.commit()
        con.close()
        
    def select_cosplayers_db(self):
        con=connect(self.database_file)
        cur=con.cursor()
        sql="SELECT * from cosplayer where info=0"
        cur.execute(sql)
        con.close()

        
    def single_execute(self,sql):
        con=sqlite3.connect(self.database_file)
        cur=con.cursor()
        res = cur.execute(sql)
        con.commit()
        con.close()
        return res
    
    def get_all_cosplayer_in_page(self,start=0):
        print("Start collecting the cosplayer in Page %d"%start)
        url="https://buondua.com/collection?start="+str(start)
        soup=self.get_soup(url)
        a_list=soup.select('.item-link')
        cosplayer_arr=[]
        for a in a_list:
            href=a.get('href')
            info=0
            saved=0

            print(href)
            # name=href.split('/')[-1]
            # path=os.path.join(self.engin_path,name)
            # os.mkdir(path)
            dct={
                'id':href,

                'info':info,
                'saved':saved
            }
            cosplayer_arr.append(dct)
        self.update_cosplayers_db(cosplayer_arr)
    
        if start<3660:
            start+=20
            self.get_all_cosplayer_in_page(start)
            
    def get_all_collections_of_cosplayer(self,href):
        url=self.base_url+href
        soup=self.get_soup(url)
        next=soup.select('.pagination-next')
        if len(next)>0:
            end=next[-1].get('href')
            end=int(end.split('=')[-1])
        else:
            end=0
        start=0
        
        collections=[]
        def get_collection_in_soup(soup):
            cs=soup.select('.item-link.popunder')
            collection=[]
            for c in cs:
                href=c.get('href')
                img=c.select('img')[0]
                img_url=img.get('data-src')
                title=img.get('alt')
                sql="INSERT or IGNORE into collection values ('%s','%s','%s',%d);"%(title,href,img_url,0)
                print("Title:%s"%title)
                collection.append(sql)
            con=connect(self.database_file)
            cur=con.cursor()
            for c in collection:
                try:
                    cur.execute(c)
                except Exception as e:
                    print("Error in execute sql:",c,e)
                continue
            con.commit()
            con.close()
        get_collection_in_soup(soup)
        start+=20
        while start<=end:
            next_url=url+"?start="+str(start)
            soup=self.get_soup(next_url)
            get_collection_in_soup(soup)
            start+=20
        return collections
    
    def update_all_cosplayer_collections(self):
        sql="select * from cosplayer where info=0"
        con=connect(self.database_file)
        cur=con.cursor()
        res=cur.execute(sql)
        all_res=[]
        for r in res:
            all_res.append(r)

        con.close()
        l=len(all_res)
        count=1
        for res in all_res:
            print("------->    %d/%d  updated "%(count,l))
            id=res[0]
            self.get_all_collections_of_cosplayer(id)
            self.update_cosplayer_collections(id)
            count+=1
            
    def get_detail_pics(self,res):
        title=res[0]
        category=title.split(' ')[0]
        cate_path=os.path.join(self.engin_path,category)
        if not os.path.exists(cate_path):
            os.mkdir(cate_path)
        
        href=self.base_url+res[1]
        post=res[2]
        total_pic_num=int(title.split('(')[-1].split(' ')[0])
        total_page=total_pic_num//20
        if total_pic_num%20!=0:
            total_page+=1
        next=2
        start=1
        con=connect(self.database_file)
        cur=con.cursor()

        path=os.path.join(cate_path,title)
        if not os.path.exists(path):
            os.mkdir(path)
        
        self.download_single(post,path,'post.jpg')
        soup=self.get_soup(href)

        def get_pic_from_soup(soup):
            print("############# start to get pic from page %d#############"%start)
            imgs=soup.select('.article-fulltext>p>img')
            count=1
            for img in imgs:
                url=img.get('data-src')
                sql="INSERT or IGNORE into pics values ('%s','%s','%s',%d);"%(url,path,str(count)+'.jpg',0)
                cur.execute(sql)
            con.commit()
            
        get_pic_from_soup(soup)
        
        while start<=next:
            start+=1
            url=href+'?page='+str(start)
            soup=self.get_soup(url)
            get_pic_from_soup(soup)
            
    def get_all_detail_pics(self):
        sql="select * from collection where saved=0"
        con=connect(self.database_file)
        cur=con.cursor()
        res=cur.execute(sql)
        results=[]
        for r in res:
            results.append(r)
        con.close()
        
        for r in results:
            print(r)
            self.get_detail_pics(r)
            title=r[0]
            sql="UPDATE collection SET saved=1 WHERE title='%s'"%(title)

            
            
    def multi_download_pic(self):
        sql="select * from pics where saved=0"
        # thread_pool=ThreadPoolExecutor(10)
        con=connect(self.database_file)
        cur=con.cursor()
        res=cur.execute(sql)
        count=100
        for r in res:
            print(r)
            count-=1
            url=r[0]
            path=r[1]
            name=r[2]
            self.download_single(url,path,name)
            sql="UPDATE pics SET saved=1 WHERE url='%s'"%(url)
            cur.execute(sql)
            if count==0:
                count=100
                con.commit()
        con.close()
   
if __name__ == '__main__':
    x=Buodua()
    x.get_all_cosplayer_in_page()
    x.update_all_cosplayer_collections()
    x.get_all_detail_pics()
    x.multi_download_pic()
