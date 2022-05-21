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
sys.path.append(os.path.abspath('./'))
import requests
from bs4 import BeautifulSoup as bs 
import threading
from engin.base import Engin

class Javday(Engin):
    def __init__(self):
        super().__init__('https://javday.tv')
        self.headers['X-Playback-Session-Id']="7D7C298F-9D13-412A-9550-37D513483C8E"
        self.headers['Referer']="https://javday.tv"
        self.engin_path = os.path.join(self.manager_path,'Javday')
        if not os.path.exists(self.engin_path):
            os.mkdir(self.engin_path)
            
    def parse_title(self,title):
        res=""
        title=title.split('/')
        for i in range(1,len(title)-2):
            res+=title[i]
        return res
        
    def get_m8u3(self,id,save="False"):
        url=self.base_url+"/videos/"+id
        soup = self.get_soup(url,debug=save)
        content = soup.select('.vcontainer>script')
        title=soup.select('title')[0].get_text()
        title=self.parse_title(title)
        
        
        if content != []:
            content=content[0].get_text()
        else:
            print("No content found.")
            return None
        if content == None:
            print("No m8u3 finded.")
            return None
        
        content = content.split('\n')
        content = [i.strip() for i in content]
        vurl = ""
        
        for l in content:
            if l.startswith("url"):
                vurl=l[6:-2]
                print(url)
            elif l.startswith("pic"):
                pic=l[6:-2]
                print(pic)
                
        pic_url = self.base_url+pic
        path = os.path.join(self.engin_path,id)
        # 尝试下载电影封面
        try:
            self.download_single(pic_url,path,title+'.jpg')
        except Exception as e:
            print("Downloading pic error:",e)
                
        if vurl!="":
            res=requests.get(vurl,headers=self.headers)
            if res.status_code<400:
                content = res.content.decode().split('\n')
                if save:
                    with open("./savetest.m8u3",'wb') as f:
                        f.write(res.content)
                return content
            else:
                print("Faild to get the m8u3 file.")
                return None
            
    
    def get_tss(self,content,path):
        tss=[]
        tss_for_write=""
        for l in content:
            if l.startswith('http'):
                tss.append(l)
                tss_for_write+=l.split('/')[-1]+'\n'

        tss_path=os.path.join(path,'tss.txt')
        with open(tss_path,'w') as f:
            f.write(tss_for_write)
        return tss
    
    def download_tss_to(self,tss,path,index=""):
        if not os.path.exists(path):
            os.mkdir(path)
        failed=[]

        for ts in tss:
            file_name = ts.split('/')[-1]
            file_path_name=os.path.join(path,file_name)
            if os.path.exists(file_path_name):
                print("%s is exist.")
                continue
            
            res=requests.get(ts,headers=self.headers)
            if res.status_code<400:
                with open(file_path_name,'wb') as f:
                    f.write(res.content)
                print("%s downloaded to %s."%(ts,path))
            else:
                print("%s download Failed.")
                failed.append(ts+'\n')
                
        failed_path=os.path.join(path,"failed.txt")
        if failed != []:
            with open( failed_path, 'w' ) as f:
                f.write(failed)
            print("Some files were faild, please download again.More detailes in %s"%failed_path)
            return False
        
        if failed == [] and os.path.exists(failed_path):
            os.remove(failed_path)
            return True
        
        
    def multi_download_tss_to(self,tss,path,thread_num=10):
        tsss=[]
        
        l=len(tss)
        rem = l%thread_num
        if rem!=0:
            x=l//(thread_num-1)
        else:
            x=l//thread_num
        
        count=0
        for i in range(thread_num-1):
            tmp=[]
            for j in range(x):
                tmp.append(tss[count])
                count+=1
                
            tsss.append(tmp)
        tmp=tss[x*(thread_num-1):]
        tsss.append(tmp)
        
        
        threads=[]
        index=1
        for t in tsss:
            thread=threading.Thread(target=self.download_tss_to,args=(t,path))
            print("Thread %d start .... "%index)
            index+=1
            threads.append(thread)
            thread.start()
            
        for th in threads:
            th.join()            
        print("All Downloads completed.")
            
    def try_failed_ts(self,path):
        failed_path=os.path.join(path,"failed.txt")
        with open(failed_path,'w') as f:
            tss = f.read().split("\n")
            return self.download_tss_to(tss,path)
            
    def merge_tss(self,path,name='1.mp4'):
        failed_path=os.path.join(path,"failed.txt")
        if not os.path.exists(failed_path):
            tss_file = os.path.join(path,'tss.txt')
            with open(tss_file,'r') as f:
                tmp=f.read().split('\n')
            file=name
            file=os.path.join(path,file)       
            with open(file,'wb+') as f:
                for ts in tmp:
                    if ts=="":
                        continue
                    ts_file = os.path.join(path,ts)
                    if os.path.exists(ts_file):
                        f.write(open(ts_file,'rb').read())
                    else:
                        print("%s 丢失，请重新下载")
                        return
            print("合并完成")
            
    def clear_ts_files(self,path):
        if os.path.exists(path):
            file = os.listdir(path)
            for f in file:
                if  f.endswith('.ts'):
                    os.remove(os.path.join(path,f))
        print("Clear completed of %s"%path)
                    
            
    def download_movie(self,id):
        path = os.path.join(self.engin_path,id)
        if not os.path.exists(path):
                os.mkdir(path)
        else:
            if os.path.exists(os.path.join(path,id+'.mp4')) or os.path.exists(os.path.join(path,'1.mp4')):
                print("Movie %s exist."%id)
                return 
            
        m8u3 = self.get_m8u3(id)
        if m8u3 != None:
            tss = self.get_tss(m8u3,path)
            flag = self.download_tss_to(tss,path)
            count = 5
            while flag==False:
                flag = self.try_failed_ts(path)
                count-=1
                if count ==0:
                    print("Failed in downloading TS files.")
            try:
                self.merge_tss(path)
                self.clear_ts_files(path)
            except Exception as e:
                print("Error in Merge: ",e)
                
                
    def multi_download_movie(self,id): 
        path = os.path.join(self.engin_path,id)
        if not os.path.exists(path):
                os.mkdir(path)
        else:
            if os.path.exists(os.path.join(path,id+'.mp4')) or os.path.exists(os.path.join(path,'1.mp4')):
                print("Movie %s exist."%id)
                return 
        
        m8u3 = self.get_m8u3(id)
        if m8u3 != None:
            tss = self.get_tss(m8u3,path)
            
            self.multi_download_tss_to(tss,path)
            
            # count = 5
            # while flag==False:
            #     flag = self.try_failed_ts(path)
            #     count-=1
            #     if count ==0:
            #         print("Failed in downloading TS files.")
            
            try:
                self.merge_tss(path)
                self.clear_ts_files(path)
            except Exception as e:
                print("Error in Merge: ",e)
                
                
    def get_index_page(self):
        path=os.path.join(self.engin_path,'Index')
        if not os.path.exists(path):
            os.mkdir(path)
        soup = self.get_soup(self.base_url)
        movies=soup.select('a.videoBox')
        movie_dict={}
        for m in movies:
            try:
                id=m.get("href").split('/')[-2]
                title = m.select('.title')[0].get_text()
                img = m.select('.videoBox-cover')[0].get('style')
                start=img.index("(")+1
                end=img.index(")")
                img=img[start:end]
                dct={
                    "title":title,
                    "id":id,
                    "img":img
                }
                movie_dict[id]=dct
            except Exception as e:
                print("Get information exist:",e)
                
        with open(path+"/info.json",'w') as f:
            json.dump(movie_dict,f)
            print("All movie info saved.")
        
        exist_movies=os.listdir(self.engin_path)
        for k,v in movie_dict.items():
            if k in exist_movies:
                print("%s exist."%k)
                continue
            else:
                img=v['img']
                img_url=self.base_url+img
                name=v['id']+' '+ v['title']+'.jpg'
                self.download_single(img_url,path,name)
                     
if __name__ == '__main__':
    # try:
    #     id = sys.argv[1]
    # except Exception as e:
    #     print("No id.")
    #     id = "2wrvUDq9"

    e=Javday()
    e.get_index_page()

