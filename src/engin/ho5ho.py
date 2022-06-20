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
import threading
import time

sys.path.append(os.path.abspath('./'))
from utils.common import divide_len_by_worker, get_soup,download_single, parser_url
from database.db import EngineDB
from urllib import parse
from sqlalchemy import insert,select,update,delete,Table,MetaData,Text,bindparam

class Ho5ho:
    manage_path='/Volumes/Movie/Ho5ho'
    base_url="https://www.ho5ho.com"
    headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15',
            'referer':"https://www.ho5ho.com"
            }
    
    def __init__(self,debug=False):
        if not os.path.exists(self.manage_path):
            os.mkdir(self.manage_path)

        # self.booklist_url="http://wzdhm.cc/booklist"
        self.db=EngineDB(database='image',echo=debug)
        
    def get_all_book(self):
        total_page=63
        page_url="https://www.ho5ho.com/page/"
        for i in range(1,total_page+1):
            url=page_url+str(i)
            soup=get_soup(url,proxy=True)
            books=soup.select('.page-item-detail.manga')
            dcts=[]
            for book in books:
                a=book.select('a')[0]
                href=a.get('href')
                title=a.get('title')
                img=a.select('img')[0]
                post=img.get('data-src')
                dct={
                    'href':href,
                    'title':title,
                    'post':post,
                    'visited':0
                }
                dcts.append(dct)
            self.db.insert_dcts('ho5ho_book',dcts)
            print("Page %d inserted to database."%(i))
            
    def get_all_pages(self,worker=5):
        def parser_name(name,index):
            try:
                base=int(name[:-4])
                if base>1:
                    index+=base 
                else:
                    index=index
            except:
                index=index
            
            if name.startswith('000'):
                return "%04d.jpg"%index
            elif name.startswith('00'):
                return "%03d.jpg"%index
            elif name.startswith('0'):
                return "%02d.jpg"%index
            elif name.startswith('1'):
                return "%d.jpg"%index

        def get_pages_from_res(result,index):
            l=len(result)
            count=0
            for r in result:
                count+=1
                title=r[1]
                r_url=r[0]
                post=r[2]
                path=os.path.join(self.manage_path,title)
                if not os.path.exists(path):
                    os.mkdir(path)
                download_single(post,path,'post.jpg')
                
                soup=get_soup(r_url,proxy=True)
                chapters={}
                cs=soup.select('li.wp-manga-chapter>a')
                for c in cs:
                    cname=c.get_text().split('-')[-1].strip()
                    href=c.get("href")
                    chapters[cname]=href
                
                #下载chapter
                for k,v in chapters.items():
                    chapter_path=os.path.join(path,k)
                    if not os.path.exists(chapter_path):
                        os.mkdir(chapter_path)
                    pics=[]
                    url=v
                    soup_c=get_soup(url,proxy=True)
                    pics=soup_c.select('#single-pager>option')
                    page_num=len(pics)//2
                    try:
                        pic=soup_c.select('#image-0')[0]
                    except Exception as e:
                        print("Error when geting image-0:",e)
                        continue
                    pic_url=pic.get('data-src')
                    url_path,name=parser_url(pic_url)
                    
                    for i in range(1,page_num+1):
                        try:
                            file_name=parser_name(name,i)
                            u=url_path+file_name
                        except Exception as e:
                            print("Error:",e,name,i)
                            break
                        try:
                            download_single(u,chapter_path,name=file_name,headers=self.headers)
                        except Exception as e:
                            print("Error :",e,end="!!!")
                            break

                dct={
                    'key':r_url,
                    'visited':1
                }
                
                self.db.update_dcts_href_visited('ho5ho_book',[dct])
                print("%d/%d@Thread-%d:Downloaded"%(count,l,index),'--> Database updated.')

        res=self.db.select_db('ho5ho_book','visited',0)
        pointers=divide_len_by_worker(len(res),worker)
        thrds=[]
        for i in range(worker):
            thrds.append(threading.Thread(target=get_pages_from_res,args=(res[pointers[i][0]:pointers[i][1]],i)))

        for t in thrds:
            t.start()
        
        for t in thrds:
            t.join()
   
if __name__ == '__main__':
    w=Ho5ho(debug=False)
    if len(sys.argv)==2:
        t=sys.argv[1]
    else:
        w.get_all_pages()