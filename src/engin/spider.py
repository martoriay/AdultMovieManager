# -*- encoding: utf-8 -*-
'''
@File    :   base.py
@Time    :   2022/05/17 13:58:00
@Author  :   Muyao ZHONG 
@Version :   1.0
@Contact :   zmy125616515@hotmail.com
@License :   (C)Copyright 2019-2020
@Title   :   Base Engin Class
'''

from abc import abstractmethod
import sys
import os
from wsgiref.util import request_uri

from torch import lstsq
sys.path.append(os.path.abspath('./'))
import requests
from bs4 import BeautifulSoup as bs 
import threading
import platform
import sqlite3 as db
from sqlite3 import connect
from abc import ABC 


class Spider:
    def __init__(self,path):
        self.path=path
        self.database_file=os.path.join(self.path,'database.db')
        version = "1.0.0"
        headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15',
        }

        if not os.path.exists(self.path):
            os.mkdir(self.path)
            print("Path %s Created."%self.path)
            con=connect(self.database_file)
            con.close()
            print("database %s created."%self.database_file)
            
        try:
            self.create_level_0_tb()
            self.create_level_1_tb()
            self.create_level_2_tb()
        except Exception as e:
            print("Tables exists.")
            
    def get_soup(self,url,debug=False,encoding=""):
        html=requests.get(url,headers=self.headers)
        if debug:
            print("Response:",html.status_code)
        if encoding=="":
            html.encoding = html.apparent_encoding
        else:
            html.encoding = encoding
        soup = bs(html.text,features="html.parser")
        return soup
            
    ######################TODO####################

    
    def get_level0_element(self,url,lst_selector,attr_selector,next_selector):
        soup=self.get_soup(url)
        lst=soup.select(lst_selector)
        result=[]
        for l in lst:
            single_dct={
                
            }
            for dct in attr_selector:
                name=dct['name']
                selector=dct['selector']
                index=dct['index']
                attr=dct['attr']
                if selector=="":
                    single_dct[name]=l.get(attr)
                else:
                    single_dct[name]=l.select(selector)[index].get(attr)
            result.append(single_dct)
        
        return result
    
    def update_level0_db(self,result,path):
        path=os.path.join(self.path,path)
        con=connect(self.database_file)
        cur=con.cursor()
        for r in result:
            url=r['url']
            file_name=url.split('/')[-1]
            sql="INSERT or IGNORE into level0 values ('%s','%s','%s',%d)"%(url,path,file_name,0)
            cur.execute(sql)
        con.commit()
        con.close()
        

    ## 建立数据库表，更新数据库表方法
    def single_db_commit(self,sql):
        con=connect(self.database_file)
        cur=con.cursor()
        cur.execute(sql)
        con.commit()
        con.close()
    
    def create_level_0_tb(self):
        sql="""
        CREATE TABLE level0 (
            url text primary key,
            path text,
            name text,
            saved integer
            );
        """
        self.single_db_commit(sql)
        
    def create_level_1_tb(self):
        sql="""
        CREATE TABLE level1 (
            title text primary key,
            page text,
            post text,
            saved integer
            );
        """
        self.single_db_commit(sql)
        
    def create_level_2_tb(self):
        sql="""
        CREATE TABLE level2 (
            category text primary key,
            page text,
            post text,
            saved integer
            );
        """
        self.single_db_commit(sql)
        
    def get_res_from_table(self,table,saved=0):
        sql="SELECT * from %s where saved=%d"%(table,saved)
        con=connect(self.database_file)
        cur=con.cursor()
        res = cur.execute(sql)
        result=[]
        for r in res:
            result.append(r)
        con.commit()
        con.close()
        return result
        
        
    def multi_download(self):
        pass
    
    def update_level_0(self):
        
        res=self.get_res_from_table('level1',saved=0)
        for r in res:
            pass


if __name__ == '__main__':
    detail_page="http://wzdhm.cc/chapter/24799"
    
    s=Spider("/Volumes/Movie/wzdhm")
    attr_s=[
        {
            "name":'url',
            'selector':'',
            'index':0,
            'attr':'data-original'
        }
    ]
    next_s=[
        {
            'name':'url',
            'selector':'.fanye>a',
            'index':0,
            'attr':'href'
        }
    ]
    res=s.get_level0_element(detail_page,'.comicpage>div>img',attr_s)
    s.update_level0_db(res,'test')
        
        
    
    