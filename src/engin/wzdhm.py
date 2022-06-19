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



import json
import sys

import os
import threading
import time

sys.path.append(os.path.abspath('./'))
from utils.common import get_soup,download_single
from database.db import EngineDB
from urllib import parse
from sqlalchemy import insert,select,update,delete,Table,MetaData,Text,bindparam

class Wzdhm:
    manage_path='/Volumes/Movie/Wzdhm'
    base_url="http://wzdhm.cc"
    def __init__(self,debug=False):
        if not os.path.exists(self.manage_path):
            os.mkdir(self.manage_path)

        self.booklist_url="http://wzdhm.cc/booklist"
        self.db=EngineDB(database='image',echo=debug)
        
    def get_all_book(self):
        page_end=10
        page_nonend=7
        base_url_end="http://wzdhm.cc/booklist?tag=全部&area=-1&end=1&page="
        base_url_nonend="http://wzdhm.cc/booklist?tag=全部&area=-1&end=0&page="
        for i in range(page_end):
            print("Ended Book in Page:%d"%(i+1),end='|')
            url=base_url_end+str(i+1)
            dcts=self.get_books_at_url(url,end=1)
            self.db.insert_dcts('wzdhm_book',dcts)
            print("Success.")
        print("All Ended book have saved in database.")
            
        for i in range(page_nonend):
            print("Non-Ended Book in Page:%d"%(i+1),end='|')
            url=base_url_nonend+str(i+1)
            dcts=self.get_books_at_url(url,end=0)
            self.db.insert_dcts('wzdhm_book',dcts)
            print("Success.")
        print("All book have saved in Database.")
        
    def update_end_db(self,table,dcts):
        t_table=Table(table,self.db.metadata_obj,autoload_with=self.db.engine)
        with self.db.engine.connect() as conn:
            conn.execute(
                update(t_table).where(t_table.c.id == bindparam('key')).values(over=bindparam('over')),
                dcts
            )
        return
    
    def update_end_book(self):
        page_end=10
        base_url_end="http://wzdhm.cc/booklist?tag=全部&area=-1&end=1&page="
        for i in range(page_end):
            print("Ended Book in Page:%d"%(i+1),end='|')
            url=base_url_end+str(i+1)
            self.update_end_book_at_url(url)
            print("Success.")
        print("All Ended book have saved in database.")
        
    #获取所有书
    def update_end_book_at_url(self,url):
        soup=get_soup(url,proxy=True)
        # print(soup)
        books=soup.select('ul.mh-list>li>div.mh-item')
        dcts=[]
        for book in books:
            a=book.select('a')[0]
            id=a.get('href')
            dct={
                'key':id,
                'over':1
            }
            dcts.append(dct)
        self.update_end_db('wzdhm_book',dcts)
        print("Books updated.")

    def get_books_at_url(self,url,end):
        # 获取一本书
        def get_book_from_soup(book):
            dct={}
            dct['over']=end
            a=book.select('a')[0]
            id=a.get('href')
            title=a.get('title')
            dct['id']=id
            dct['title']=title
            dct['url']=self.base_url+id
            dct['visited']=0
            dct['rate']=0
            

            post=book.select('a>p.mh-cover')[0].get('style')
            start=post.index('(')+1
            post=post[start:-1]
            dct['post']=post
            
            c=book.select('p.chapter>a')[0].get_text()
            dct['total_chapter']=c
            return dct
            
        soup=get_soup(url,proxy=True)
        # print(soup)
        books=soup.select('ul.mh-list>li>div.mh-item')
        dcts=[]
        for book in books:
            # print(book)
            dct=get_book_from_soup(book)
            dcts.append(dct)
        return dcts
    
    def get_chapters_from_book(self):
        res=self.db.select_db('wzdhm_book','visited',0)
        l=len(res)
        count=0
        for r in res:
            count+=1
            print("%d/%d:Get chapters of %s--->"%(count,l,r[1]),end='')
            try:
                self.get_chapters_from_res(r)
                print("Success.")
            except Exception as e:
                print("Failed with Error:%s"%e)
        print("All chapters updated.")

    def get_chapters_from_res(self,r):
        def get_chapter(chapter):
            index=chapter.get('idx')
            a=chapter.select('a')[0]
            href=a.get('href')
            title=a.get_text()
            dct={
                'index':index,
                'id':href,
                'url':self.base_url+href,
                'title':title,
                'path':title,
                'visited':0
            }
            return dct
        
        def get_info(info):
            subtitles=info.select('p.subtitle')
            if len(subtitles)==2:
                alias=subtitles[0].get_text()
                author=subtitles[1].get_text()
            else:
                alias="Unknow"
                author="Unknow"
            tip=info.select('p.tip>span')
            end=1
            update_time=""
            tag=""
            for s in tip:
                t=s.get_text()
                if "已完结" in t:
                    end=1
                elif t.startswith('更新时间'):
                    t=t.split('：')[-1]
                    update_time=t
                elif t.startswith('标签'):
                    tag=t
            try:
                intro=info.select('p.content>span>span')[0].get_text()
            except:
                intro="Unknow"
                
            dct={
                'alias':alias,
                'author':author,
                'over':end,
                'update_time':update_time,
                'tag':tag,
                'intro':intro
            }
            return dct
            
        # id,title,post,url,visited,rate,over,total_chapter=r
        id=r[0]
        title=r[1]
        url=r[3]

        book_path=os.path.join(self.manage_path,title)
        if not os.path.exists(book_path):
            os.mkdir(book_path)
        soup=get_soup(url,proxy=True)
        chapters=soup.select('#detail-list-select>li')
        dcts_chapter=[]
        for chapter in chapters:
            dct=get_chapter(chapter)
            dct['bid']=id 
            dct['path']=os.path.join(book_path,dct['path'])
            dcts_chapter.append(dct)
        self.db.insert_dcts('wzdhm_chapter',dcts_chapter)
        print("Chapter Updated",end="->")
        
        info=soup.select('.info')[0]
        dct_info=get_info(info)
        
        dct_info['key']=id 
        dct_info['visited']=1
        self.update_info_db('wzdhm_book',dct_info)
        
        print("Info updated",end="->")
        
    def update_chapters_from_res(self,r):
        def get_chapter(chapter,index):
            a=chapter.select('a')[0]
            href=a.get('href')
            dct={
                'index':index,
                'key':href,
            }
            return dct
        def update_chapter_db(table,dcts):
            t_table=Table(table,self.db.metadata_obj,autoload_with=self.db.engine)
            with self.db.engine.connect() as conn:
                conn.execute(
                    update(t_table).where(t_table.c.id == bindparam('key')).values(index=bindparam('index')),
                    dcts
                )
            return
        
        url=r[3]
        index=0

        soup=get_soup(url,proxy=True)
        chapters=soup.select('#detail-list-select>li')
        dcts_chapter=[]
        for chapter in chapters:
            index+=1
            dct=get_chapter(chapter,index)
            dcts_chapter.append(dct)
        update_chapter_db('wzdhm_chapter',dcts_chapter)
        print("Chapter Updated",end="->")
        
    def update_chapter_index(self):           
        res=self.db.select_db('wzdhm_book','visited',1)
        l=len(res)
        count=0
        for r in res:
            count+=1
            print("%d/%d:Get chapters of %s--->"%(count,l,r[1]),end='')
            try:
                self.update_chapters_from_res(r)
                print("Success.")
            except Exception as e:
                print("Failed with Error:%s"%e)
        print("All chapters updated.")
        
        
    def update_info_db(self,table,dcts):
        t_table=Table(table,self.db.metadata_obj,autoload_with=self.db.engine)
        with self.db.engine.connect() as conn:
            conn.execute(
                update(t_table).where(t_table.c.id == bindparam('key')).values(
                    alias=bindparam('alias'),
                    author=bindparam('author'),
                    over=bindparam('over'),
                    update_time=bindparam('update_time'),
                    tag=bindparam('tag'),
                    intro=bindparam('intro'),
                    visited=bindparam('visited')
                    ),
                dcts
            )
        return
    
    # def mk_book_dir(self):
    #     res=self.db.select_db('wzdhm_book','visited',1)
    #     for r in res:
    #         title=r[1]
    #         path
    
    def get_pics_from_chapter(self,worker=7):
        def get_pic_from_ress(ress,index):
            l=len(ress)
            count=0
            for r in ress:
                count+=1
                print("%d/%d@Thread-%d:Get Pics of %s--->"%(count,l,index,r[1]),end='')
                try:
                    self.get_pics_from_res(r)
                    print("Success.")
                except Exception as e:
                    print("Failed with Error:%s"%e)
                    
        res=self.db.select_db('wzdhm_chapter','visited',0)
        l=len(res)
        points=[round(i/worker*l) for i in range(worker)]
        thrds=[]
        for i in range(worker-1):
            thrds.append(threading.Thread(target=get_pic_from_ress,args=(res[points[i]:points[i+1]],i+1)))
        thrds.append(threading.Thread(target=get_pic_from_ress,args=(res[points[-1]:],worker)))
        
        for t in thrds:
            t.start()
        for t in thrds:
            t.join()
        
    def get_pics_from_res(self,r):
        id=r[0]
        title=r[2]
        url=r[4]
        path=r[5]
        if not os.path.exists(path):
            os.mkdir(path)
        
        soup=get_soup(url,proxy=True)
        pics=soup.select('div.comicpage>div>img')
        all_pic=[]
        for p in pics:
            all_pic.append(p.get('data-original'))
        print("Start download:%s"%title,end='->')
        self.download_pic_list(all_pic,path)
        dct={
            'key':id,
            'visited':1
        }
        self.update_chapter_db('wzdhm_chapter',dct)
        print("database updated",end='-> ')
        
    def update_chapter_db(self,table,dcts):
        t_table=Table(table,self.db.metadata_obj,autoload_with=self.db.engine)
        with self.db.engine.connect() as conn:
            conn.execute(
                update(t_table).where(t_table.c.id == bindparam('key')).values(visited=bindparam('visited')),
                dcts
            )
        return
        
        
    def download_pic_list(self,pic_list,path):
        l=len(pic_list)
        for i in range(l):
            pic=pic_list[i]
            name=str(i+1)+'.jpg'
            download_single(pic,path,name,proxy=True,debug=False)
        print("Done.",end="|")
            

        
if __name__ == '__main__':
    w=Wzdhm(debug=False)
    if len(sys.argv)==2:
        t=sys.argv[1]
        if t=='fix':
            w.update_chapter_index()
    else:
        w.get_pics_from_chapter()
    

        
        