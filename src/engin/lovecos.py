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

import sys
import os
sys.path.append(os.path.abspath('./'))
import time

from engin.base import Engin
# import tkinter as tk 
# from tkinter import *
# from tkinter import messagebox

import sqlite3

class Lovecos(Engin):
    def __init__(self):
        self.engin_path='/Volumes/Movie/'
        super().__init__('http://www.lovecos.net')
        # self.headers['X-Playback-Session-Id']="7D7C298F-9D13-412A-9550-37D513483C8E"
        self.engin_path = os.path.join(self.manager_path,'Lovecos')
        if not os.path.exists(self.engin_path):
            os.mkdir(self.engin_path)
        self.database_file=os.path.join(self.engin_path,'lovecos.db')
        if not os.path.exists(self.database_file):
            self.create_db()
            print("Database lovecos.db created.")

        self.categories=[
            "gamecos",
            "chinacos",
            "japancos",
            "hotcosplay"       
        ]
        
    def create_db(self):
        sql="""
        CREATE TABLE cosplay (
            id text primary key, 
            title text, 
            pic text,
            saved integer);
        """
        self.single_execute(sql)
        print("Table cosplay created.")
        
    def create_tb(self,name):
        check_sql="SELECT count(*) FROM sqlite_master WHERE type='table' AND name='%s'"%name
        res=self.single_execute(check_sql)
        if res!=0:
            return 

        sql="""
        CREATE TABLE %s (
            id text primary key, 
            title text, 
            pic text,
            saved integer);
        """%name
        self.single_execute(sql)
        self.commit()
        print("Table cosplay created.")
        
            
    def single_execute(self,sql):
        con=sqlite3.connect(self.database_file)
        cur=con.cursor()
        res = cur.execute(sql)
        con.commit()
        con.close()
        return res
        
        
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
    
    def exist_or_insert_single(self,dct,table='cosplay'):
        sql="INSERT or IGNORE into %s values ( '%s','%s','%s',%d);"%(table,dct['id'],dct['title'],dct['pic'],dct['saved'])
        try:
            self.single_execute(sql)
            print(dct['id']," have been inserted to table")
        except Exception as e:
            print("Error when insert %s:"%dct[id],e)
        
        
    def exist_or_insert_multi(self,dcts,table='cosplay'):
        values=""
        for i in range(len(dcts)):
            dct=dcts[i]
            self.exist_or_insert_single(dct,table)
        flag=self.commit()
        if flag==True:
            print("All dcts have been inserted into the cosplay table.")
            return
        

        time.sleep(5)
        
        try:
            self.exist_or_insert_multi(dcts,table)
        except Exception as e:
            print("Error when reconnect to the database:",e)
        

        
        
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
    
    def insert_page_list_into_database(self,url,table):
        lst=self.get_page_pic_list(url)
        dcts=self.get_dcts_from_lst(lst)
        self.exist_or_insert_multi(dcts,table)

    def insert_all_pages(self,category,start=1):
        self.create_tb(category)
        url=self.base_url+'/'+category+'/'
        
        soup=self.get_soup(url)
        page=soup.select('.page>a')[-1].get('href')
        last=page.split('/')[-2]
        last=int(last)
        for i in range(start,last):
            print("############  Start insert page: %d ############"%i)
            page_url=url+str(i)+'/'
            self.insert_page_list_into_database(page_url,table='cosplay')

            
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

    #     note.pack()
    #     if single:
    #         root.mainloop()
    #     else:
    #         return note
        
    # ?????????????????????????????????????????????????????????
    
    def create_fold_and_download_pic(self,r,table):
        
        id=r[0]
        tmp=id[1:-5].split('/')
        
        cat=tmp[0]
        cat_path=os.path.join(self.engin_path,cat)
        if not os.path.exists(cat_path):
            os.mkdir(cat_path)
        iid=tmp[1]
        pic_path=os.path.join(self.engin_path,cat,iid)
        if not os.path.exists(pic_path):
            os.mkdir(pic_path)
        
        title=r[1]
        pic=r[2]
        saved=r[3]
        
        self.download_single(pic,pic_path,'post.jpg')
        
        url=self.base_url+id
        pics_num=self.get_detail_pic(url,pic_path)
        saved+=pics_num
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
        pages_soup=self.get_soup(url).select('.page>a')
        
        pages=[url]
        pre,_=self.parse_url_to_pre_and_file(url)
        if len(pages_soup)!=0:
            for p in pages_soup:
                pages.append(pre+p.get('href'))
            
        pics=[]
        for p in pages:
            pic_soup=self.get_soup(p).select('.mtp>li>a>img')
            for img in pic_soup:
                img_url=img.get('src')
                name=img.get('alt')
                pics.append((name,self.mid_pic_to_large_pic(img_url)))
        
        for pname,purl in pics:
            self.download_single(purl,path,pname+'.jpg')
        return len(pics)
            
    def mid_pic_to_large_pic(self,url):
        pre,file=self.parse_url_to_pre_and_file(url)
        return pre+file[1:]
        
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
    l=Lovecos()
    # l.insert_all_pages(l.categories[3])
    # l.insert_page_list_into_database("http://www.lovecos.net/gamecos/")
    # l.ui()
    # l.get_all_pics_from_database('cosplay')
    # pics=l.get_detail_pic("http://www.lovecos.net/chinacos/50786.html","")
    # print(pics)
    
    finish=False
        
    while finish==False:
        try:
            finish=l.get_all_pics_from_database('cosplay')      
        except Exception as e:
            print("Error: ",e)
            time.sleep(20)

            
    

         
    