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
import time

sys.path.append(os.path.abspath('./'))
from utils.common import get_soup
from database.db import EngineDB
from urllib import parse


class Xnxx:
    manage_path="/Volumes/Movie/Xnxx"
    
    def __init__(self):
        self.base_url="https://www.xnxx.com"
        self.test_url="https://www.xnxx.com/video-15bwr32d/_jk"
        self.categories=[
            ''
        ]
        self.db=EngineDB()
    
    def initiate(self):
        soup=get_soup(self.base_url,proxy=True)

        ass=soup.select('ul.side-cat-list>li>a')

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
        l=len(res)
        count=0
        for r in res:
            count+=1
            print("%d/%d"%(count,l),end="-->")
            url=r[0]
            category=r[2]
            print("Page: %s --> %s "%(parse.unquote(category),parse.unquote(url)),end=" --> ")
            try:
                soup=get_soup(url,proxy=True)
                dcts=self.get_video_from_soup(soup,category)
                self.db.insert_dcts('xnxx',dcts)
                update_dct={
                    'key':url,
                    'value':1
                }
                self.db.update_dcts_xnxx('xnxxpage',[update_dct])
                print("Success.")
            except Exception as e:
                print("Failed:%s",e)

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
                # print("Error to get uploader:",e)
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
                'duration':0,
                'visitors':visitor,
                'upvote':'0',
                'visited':0,
                'vid':id,
                'rate':0,
                'superfluous':superfluous 
            }
            dcts.append(dct)
        return dcts
    
    def get_detail_info_video(self,res):
        
        vid=res[10]
        url=res[11]
        result={'key':vid,'visited':1}
        full_url=self.base_url+url
        try:
            category=parse.unquote(res[5])
        except:
            category=res[5]
        
        path=category.split('/')[-1]
        
        category_path=os.path.join(self.manage_path,path)
        if not os.path.exists(category_path):
            os.mkdir(category_path)
            
        folder=os.path.join(category_path,vid)
        result['folder']=folder
        # post=res[1]
        print("Task: %s --> %s"%(res[0],path),end='   |||  ')
        soup=get_soup(full_url,proxy=True)
        
        try:
            result['superfluous']=soup.select('.rating-box.value')[0].get_text()
        except:
            result['superfluous']="Unknow"
        
        try:
            result['upvote']=soup.select('.vote-action-good')[0].get_text()
        except:
            result['upvote']='Unknow'
        
        try:
            result['visitors']=soup.select('span.metadata')[0].get_text().split('-')[-1].strip()
        except:
            result['visitors']='Unknow'
            
        ss=soup.select('#video-player-bg>script')
        if len(ss)!=6:
            return
        related=ss[0].get_text()
        
        relateds_arr=self.get_related(related)
        video=ss[3].get_text()
        video_dct=self.get_video(video)
        metas=soup.select('meta')
        meta_dct=self.get_meta(metas)
        
        result.update(video_dct)
        result.update(meta_dct)
        result['related']=json.dumps(relateds_arr)
        
        return result
        
    def get_meta(self,metas):
        dct={}
        for meta in metas:
            n=meta.get('name')
            p=meta.get('property')
            if n=='keywords':
                tag=meta.get('content')
                dct['tag']=tag
            if p=="og:duration":
                d=meta.get('content')
                try:
                    d=int(d)
                except:
                    d=0
                dct['duration']=d
        return dct

    def get_video(self,video_text):
        text=video_text.split('\n')
        text=[t.strip() for t in text]
        video_hight=""
        video_hls=""
        video_thumb=""
        video_slides=""
        video_id=""
        
        for t in text:
            if t.startswith("html5player.setVideoUrlHigh"):
                video_hight=t[29:-3]
            if t.startswith("html5player.setVideoHLS"):
                video_hls=t[25:-3]
            if t.startswith("html5player.setThumbUrl"):
                video_thumb=t[25:-3]
            if t.startswith("html5player.setThumbSlideBig"):
                video_slides=t[30:-3]
            if t.startswith("var html5player = new HTML5Player"):
                video_id=t[49:-3]
            
        dct={
            'mp4':video_hight,
            'm3u8':video_hls,
            'thumb':video_thumb,
            'slides':video_slides,
            'id':video_id
        }
        return dct 
    
    def get_related(self,related_text):
        start=related_text.index('[')
        end=related_text.index(']')
        tmp=related_text[start:end+1]
        try:
            related=json.loads(tmp)
        except:
            return []
        relateds=[]
        for r in related:
            relateds.append(self.parse_related(r))
        
        return relateds

    def parse_related(self,r):
        dct={
            'id':r['id'],
            'url':r['u'],
            'post':r['i'],
        }
        return dct
        
    def update_xnxx(self,visited=0):
        result=self.db.select_db('xnxx','visited',visited)
        l=len(result)
        count=0
        for res in result:
            count+=1
            print("%d/%d"%(count,l),end=":  ")
            try:
                r=self.get_detail_info_video(res)
            except Exception as e:
                print("Error: %s"%e)
                print("RES:",res)
                time.sleep(2)
                continue
            try:
                self.db.update_dcts_xnxx_detail('xnxx',r)
                print("Success.")
            except Exception as e:
                print("Failed:%s",e)
                continue
        
if __name__ == '__main__':
    x=Xnxx()
    if len(sys.argv)>1:
        arg=sys.argv[1]
    else:
        arg=""
        
    if arg=="":
        x.update_pages()
    else:
        x.update_xnxx(visited=0)
