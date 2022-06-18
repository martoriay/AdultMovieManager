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


from concurrent.futures import ThreadPoolExecutor
import json
import sys

import os
from pexpect import ExceptionPexpect

sys.path.append(os.path.abspath('./'))
import requests
import time
from bs4 import BeautifulSoup as bs 
import threading
from threading import Lock
from engin.base import Engin
from functools import partial
from concurrent.futures import ThreadPoolExecutor
from utils.common import get_soup
import sqlalchemy,json
from sqlalchemy import BIGINT, VARCHAR, Column, Integer, BOOLEAN, bindparam,create_engine
from sqlalchemy import text as sqltext
from sqlalchemy import insert,select,update,delete,Table,MetaData,Text
from database.db import EngineDB 

class Xnxx:
    def __init__(self):
        self.base_url="https://www.xnxx.com"
        self.test_url="https://www.xnxx.com/video-15bwr32d/_jk"
        self.categories=[
            ''
        ]
        self.db=EngineDB()
    
    def initiate(self):
        soup=get_soup(self.base_url,proxy=True)
        print(soup)
        ass=soup.select('ul.side-cat-list>li>a')
        print(ass)
        hrefs={}
        for a in ass:
            href=a.get('href')
            title=a.get('title')
            if '?' in href:
                i=href.index('?')
                href=href[:i]
            hrefs[href]=title
        with open('categories.txt', 'w') as f:
            json.dump(hrefs,f)
        print("all categories dumped.")
        
    def get_all_pages(self):
        with open('categories.json','r') as f:
            tmp=json.load(f)
        
        with open('visited_categories.json','r') as f:
            visited=json.load(f)

        for k,v in tmp.items():
            if k in visited:
                continue
            try:
                self.get_total_pages(k,v)
                visited.append(k)
            except Exception as e:
                print("Error : ",e)
                with open('visited_categories.json','w') as f:
                    json.dump(visited,f)
                return
        print("all categories' page have inserted into the database.")

        
    def get_total_pages(self,category,title):
        # if category.startswith('http'):
        #     return 
        if not category.startswith('/search/'):
            return 
        
        url=self.base_url+category
        soup=get_soup(url,proxy=True)
        # return soup
        # print(soup)
        last=soup.select('a.last-page')
        # print(last)
        if len(last)>0:
            last=last[0]
            # print("Last:",last)
        else:
            last=soup.select('.pagination>ul>li>a')[-2]
            print("No last page.")
            return 
        
        try:
            last_page_num=int(last.get_text())
        except Exception as e:
            print("Get last page of %s run, set 10 as default."%category)
            last_page_num=20
        
        
        dcts=[]

        for i in range(last_page_num):
            if i==0:
                page_url=self.base_url+category
            else:
                page_url=self.base_url+category+'/'+str(i)
            dct={
                'category':category,
                'page_num':i,
                'visited':0,
                'url':page_url,
                'rate':0,
                'title':title
            }
            dcts.append(dct)
        self.db.insert_dcts('xnxxpage',dcts)
        print("%s | % s   Pages have been iserted to Database."%(category,title))
        
    def update_pages(self):
        res=self.db.select_db('xnxxpage','visited',0)
        for r in res:
            print(r)
            url=r[0]
            category=r[2]
            soup=get_soup(url,proxy=True)
            dcts=self.get_video_from_soup(soup,category)
            self.db.insert_dcts('xnxx',dcts)
            print("Page ||%s --> %s || Info have insert into Xnxx"%(category,url))
            update_dct={
                'key':url,
                'value':1
            }
            self.db.update_dcts_xnxx('xnxxpage',[update_dct])

    def get_video_from_soup(self,soup,category):
        videos_div=soup.select('.mozaique>div')
        dcts=[]
        for video_div in videos_div:
            id=video_div.get('id')
            if id=="" or id is None:
                continue
            a=video_div.select('a')[0]
            img=video_div.select('img')[0]
            post=img.get('data-src')
            url=a.get('href')
            try:
                uploader=video_div.select('.uploader>a')[0].get('href')
            except Exception as e:
                print("Error to get uploader:",e)
                uploader="unknown"
            undera=video_div.select('.thumb-under>p>a')[0]
            title=undera.get('title')
            try:
                meta=video_div.select('.metadata')[0].get_text()
                meta=meta.strip()
                tmp,t=meta.strip('\n')
                visitor,superfluous=tmp.split(' ')
            except:
                t="10m"
                visitor='0'
                superfluous='0%'
            
            dct={
                'url':url,
                'title':title,
                'post':post,
                'm3u8':"",
                'tag':'',
                'related':'',
                'category':category,
                'author':uploader,
                'time':t,
                'visitors':visitor,
                'upvote':'0',
                'visited':0,
                'vid':id,
                'rate':0,
                'superfluous':superfluous 
            }
            dcts.append(dct)
        return dcts

if __name__ == '__main__':
    x=Xnxx()
    # x.get_all_pages()
    x.update_pages()
    



        