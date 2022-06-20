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
import requests

class Reddit:
    manage_path="/Volumes/Movie/Reddit"
    base_url="http://www.reddit.com"
    headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15',
            }
    proxies={
        'http':'http://127.0.0.1:7890',
        'https':'http://127.0.0.1:7890'
    }
    
    def __init__(self,debug=False):
        if not os.path.exists(self.manage_path):
            os.mkdir(self.manage_path)

        self.db=EngineDB(database='news',echo=debug)
        
    def get_comments(self,sub,q,after="Start"):
        while after:
            print("After:",after)
            # if after=="Start":
            #     url=self.base_url+'/r/'+sub+"/search.json?q="+q+'&restrict_sr=1&t=all&type=link&limit=100&sort=new'
            # else:
            #     url=self.base_url+'/r/'+sub+"/search.json?q="+q+'&restrict_sr=1&t=all&type=link&limit=100&sort=new&after='+after
            # if after=="Start":
            #     url=self.base_url+"/search.json?q="+q
            # else:
            #     url=self.base_url+"/search.json?q="+q+'&after='+after
            
            url=self.base_url+'/r/'+sub+"/search.json?q="+q+'&restrict_sr=1&t=all&type=link'
            res=requests.get(url,headers=self.headers,proxies=self.proxies)
            # soup=get_soup(url,proxy=True)
            # j=soup.json()
            j=res.json()
            data=j['data']
            articles=data['children']
            after=data['after']
            dcts=[]
            
            for article in articles:
                d=article['data']
                title=d['title']
                author=d['author_fullname']
                created=d['created']
                id=d['id']
                # print("ID:",id)
                if not id:
                    continue
                url=d['url']
                # if url.startswith('https'):
                #     continue
                # images=[]
                try:
                    dd=d['crosspost_parent_list'][0]['media_metadata']
                except:
                    try:
                        dd=d['media_metadata']
                    except:
                        print("Error:",url)
                        # print(d)
                        continue
                if type(dd)==list:
                    dd=dd[0]
                # for k,v in dd.items():
                images=list(dd.keys())
                # print("Image:",images)
                # print(images)
                dct={
                    'id':id,
                    'title':title,
                    'author':author,
                    'utc':created,
                    'images':json.dumps(images),
                    'keyword':q,
                    'url':url,
                }
                dcts.append(dct)
            if dcts!=[]:
                self.db.insert_dcts('reddit_sub',dcts)
            print("Database updated.")
            # break
        
    def get_pics_from_ids(self,ids,path):
        failed=[]
        for i in range(len(ids)):
            id=ids[i]
            file_name="%03d-%s.jpg"%(i,id)
            url="https://i.redd.it/%s.jpg"%id
            c=download_single(url,path=path,name=file_name,proxy=True)
            if c>=400:
                url="https://i.imgur.com/%s.jpg"%id
                c=download_single(url,path=path,name=file_name,proxy=True)
                if c>=400:
                    failed.append(id)
                    with open(os.path.join(path,file_name)+'-failed','w') as f:
                        print("Error faile.")


        print("Success.",end='-->')
        return failed
        
    def get_all_pics(self):
        res=self.db.select_db('reddit_sub','visited',0)
        
        for r in res:
            id=r[0]
            title=r[2]
            url=r[1]
            if url.startswith('http'):
                pass
            if url.startswith('/'):
                url="https://www.reddit.com"+url
            info=self.get_detail_text(url)
            ids=json.loads(r[7])
            path=os.path.join(self.manage_path,title)
            if not os.path.exists(path):
                os.mkdir(path)
            print("Try to get %s images:"%title,end='-->')
            failed=self.get_pics_from_ids(ids,path)
            dct={
                'key':id,
                'info':json.dumps(info)
            }
            if len(failed)>0:
                dct['images']=json.dumps(failed)
                dct['visited']=1
            else:
                dct['visited']=3
            self.db.update_id_key_costum_value('reddit_sub',[dct])
            print("Database updated.")
            
    

    def get_detail_text(self,url):
        soup=get_soup(url,proxy=True)
        ps=soup.select('p')
        info=[]
        for p in ps:
            t=p.get_text()
            info.append(t)
        return info
    
    def get_all_detail_text(self,visited=2):
        res=self.db.select_db('reddit_sub','visited',visited)
        for r in res:
            id=r[0]
            title=r[2]
            url=r[1]
            if url.startswith('http'):
                pass
            if url.startswith('/'):
                url="https://www.reddit.com"+url
            info=self.get_detail_text(url)
            dct={
                'key':id,
                'info':json.dumps(info),
                'visited':3
            }
            self.db.update_id_key_costum_value('reddit_sub',[dct])
            print("Info updated in database.")
              

if __name__ == '__main__':
    r=Reddit()
    if len(sys.argv)>=2:
        c=sys.argv[1]
        if c=='pic':
            r.get_all_pics()
        elif c=='info':
            # r.get_all_detail_text(0)
            r.get_all_detail_text(1)
            # r.get_all_detail_text(2)
    else:
        for i in range(1,100):
            print("Start->index:%d"%i)
            r.get_comments('hanren','翻车新闻 vol %d'%i)
    # ids=['e3s86i9yg7591', 'ug86rh3yg7591', 'tsx3ti9yg7591', 'iqxo8i3yg7591', '0ep5li9yg7591', 'wvpiil9yg7591', 'gm3a7i9yg7591', '7kbhgh3yg7591', 'fo44qh9yg7591', 'hmv93i3yg7591', 'a8ht1h3yg7591', 'jzzjbi9yg7591', 'x8btnj9yg7591', 'lzcm9i3yg7591', 'm1bh5i9yg7591', 'n7d54i9yg7591']
    
    # r.get_pics_from_ids(ids,'./img')
    # r.get_all_pics()
                    



            