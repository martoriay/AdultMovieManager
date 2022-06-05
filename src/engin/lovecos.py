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
import sys
import os
from unicodedata import category
import pyperclip
sys.path.append(os.path.abspath('./'))
import requests
import time
from bs4 import BeautifulSoup as bs 
import threading
from engin.base import Engin
import tkinter as tk 
from tkinter import *
from tkinter import messagebox
from functools import partial
import sqlite3

class Lovecos(Engin):
    def __init__(self):
        super().__init__('http://www.lovecos.net')
        # self.headers['X-Playback-Session-Id']="7D7C298F-9D13-412A-9550-37D513483C8E"
        self.engin_path = os.path.join(self.manager_path,'Lovecos')
        if not os.path.exists(self.engin_path):
            os.mkdir(self.engin_path)
        self.database_file=os.path.join(self.engin_path,'lovecos.db')
        if not os.path.exists(self.database_file):
            self.create_db()
            print("Database lovecos.db created.")
            
        self.con=sqlite3.connect(self.database_file)

        self.categories=[
            "gamecos",
            "chinacos",
            "japancos",
            "hotcos"       
        ]
        
    def create_db(self):
        sql="""
        CREATE TABLE cosplay (
            id text primary key, 
            title text, 
            pic text,
            saved integer);
        """
        self.execute(sql)
        print("Table cosplay created.")
        
    def execute(self,sql):
        con = sqlite3.connect(self.database_file)
        cur=con.cursor()
        cur.execute(sql)
        con.commit()
        con.close()

        
    def continue_execute(self,cur,sql):
        cur.execute(sql)
        
    def from_single_soup_to_dict(self,pic):
        a=pic.select('.p_title>a')[0]
        # tmp=a.get('href')[1:-5].split('/')
        # id=tmp[1]
        # category=tmp[0]
        id=a.get('href')
        title=a.get('title')
        baned_char=["'"]
        title2=""
        for c in title:
            if c not in baned_char:
                title2+=c 
        ppic=pic.select('img')[0].get('src').strip()
        dct={
            'id':id,
            # 'category':category,
            'title':title2,
            'pic':ppic,
            'saved':0
        }
        return dct
    
    def exist_or_insert_single(self,dct):
        sql="INSERT or IGNORE into cosplay values ( '%s','%s','%s',%d);"%(dct['id'],dct['title'],dct['pic'],dct['saved'])
        try:
            self.execute(sql)
            print(dct['id']," have been inserted to table")
        except Exception as e:
            print("Error when insert %s:"%dct[id],e)
        
        
    def exist_or_insert_multi(self,dcts):
        values=""
        for i in range(len(dcts)):
            dct=dcts[i]
            self.exist_or_insert_single(dct)
        #     tmp="('%s','%s','%s',%d)"%(dct['id'],dct['title'],dct['pic'],dct['saved'])
        #     if i!=len(dcts):
        #         tmp+=','
        #     else:
        #         tmp+=';'
        #     values+=tmp 
        # sql="INSERT or IGNORE into cosplay VALUES %s"%values 
        # self.execute(sql)
        print("All dcts have been inserted into the cosplay table.")
        
    def get_page_pic_list(self,url):
        soup=self.get_soup(url)
        lst=self.get_content_from_soup(soup,'.cdiv>ul>li')
        return lst
    
    def get_dcts_from_lst(self,lst):
        dcts=[]
        for pic in lst:
            dct=self.from_single_soup_to_dict(pic)
            dcts.append(dct)
        return dcts 
    
    def insert_page_list_into_database(self,url):
        lst=self.get_page_pic_list(url)
        dcts=self.get_dcts_from_lst(lst)
        self.exist_or_insert_multi(dcts)

    def insert_all_pages(self,category):
        url=self.base_url+'/'+category+'/'
        
        soup=self.get_soup(url)
        page=soup.select('.page>a')[-1].get('href')
        last=page.split('/')[-2]
        last=int(last)
        for i in range(3,last):
            print("############  Start insert page: %d ############"i)
            page_url=url+str(i)+'/'
            self.insert_page_list_into_database(page_url)
            
    def ui(self,root=None):
        if root==None:
            root=tk.Tk()
            root.geometry('800x480')
        
        
        
if __name__ == '__main__':
    l=Lovecos()
    l.insert_all_pages(l.categories[0])
    # l.insert_page_list_into_database("http://www.lovecos.net/gamecos/")
    

         
    