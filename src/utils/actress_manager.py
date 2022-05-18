# -*- encoding: utf-8 -*-
'''
@File    :   manager_actress.py
@Time    :   2022/05/17 19:53:30
@Author  :   Muyao ZHONG 
@Version :   1.0
@Contact :   zmy125616515@hotmail.com
@License :   (C)Copyright 2019-2020
@Title   :   Actresses Manager

'''

import sys,json,subprocess
import os,time
import threading


import pyperclip
sys.path.append(os.path.abspath('./'))

import tkinter as tk 
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup as bs 

from tkinter import *
from tkinter import ttk
from PIL import Image,ImageTk
from utils.movie import Movie,AllMovieInfo

from functools import partial

class ActressManager:
    manager_path = "/Volumes/Movie/Manager/Actresses"
    actresses_url= "https://www.r18.com/videos/vod/movies/actress/?page=%d&lg=zh"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
    }
    total_page_num = 344
    
    def get_actresses_in_page(self,page_num):
        url = self.actresses_url%page_num
        response = requests.get(url,headers=self.headers)
        response.encoding = response.apparent_encoding
        soup = bs(response.text,features="html.parser")
        actresses = soup.select("ul.nml07>li")
        
        actresses_dict=[]
        for  actress in actresses:
            actresses_dict.append(self.get_actress_dct_from_soup(actress))
        file_name="actresses_page_"+str(page_num)+".json"
        self.save_actresses_dict(actresses_dict,"JsonInfo",file_name)
            
            
    def get_actress_dct_from_soup(self,actress):
        url = actress.select("a")[0].get('href')
        img = actress.select("img")[0].get('src')
        name  = actress.select("div.txt01")[0].text.strip()
        start = url.index("id=")
        end = url.index("&type")
        id = url[start+3:end]
        en_name = img.split('/')[-1].split('.')[0]
        
        return {
            "url":url,
            "img":img,
            "name":name,
            "id":id,
            "en_name":en_name
        }
        
    def get_actress_from_json(self,page_num):
        path=os.path.join(self.manager_path,"JsonInfo","actresses_page_%d.json"%page_num)
        with open(path,'r') as f:
            actresses = json.load(f)
        return actresses
        
    def download_actresses_in_list(self,list):
        l = len(list)
        count=1
        for item in list:
            print("Actress %d/%d :"%(count,l))
            actress = Actress(item)
            actress.download_all_resources()
            count+=1
            time.sleep(5)
        
    def  save_actresses_dict(self,js,path,file):
        path = os.path.join(self.manager_path,path)
        if not os.path.exists(path):
            os.mkdir(path)
        file_name = os.path.join(path,file)
        with open(file_name,'w') as f:
            json.dump(js,f)
            print("Json file dump to %s"%(file_name))
            
        
    def update_all(self):
        for i in range(self.total_page_num):
            print("Start get Page %d:"%(i+1),end="||")
            self.get_actresses_in_page(i+1)
            time.sleep(5)
              


class Actress:
    actresses_path="/Volumes/Movie/Manager/Actresses"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
    }
    download_count = 60
    sleep_time = 60
    def __init__(self,dct):
        self.url = dct['url']
        self.img = dct['img']
        self.name = dct['name']
        self.en_name = dct['en_name']
        self.id = dct['id']
        self.movies_dict={}
        self.actress_path=os.path.join(self.actresses_path,self.id+"-"+self.en_name)
        
    def get_all_movies(self):
        if not os.path.exists(self.actress_path):
            os.mkdir(self.actress_path)
        page_num=1
        flag=False
        while not flag:
            flag=self.get_movies_from_page(page_num)
            # self.save_movies_dict(self.movies_dict,self.actress_path,self.en_name+'.json')
            page_num+=1
            # break
        self.save_movies_dict(self.movies_dict,self.actress_path,self.en_name+'.json')
        return
            
        
    def get_movies_from_page(self,page_num):
        url = self.url+"&page="+str(page_num)+"&lg=zh"
        print("Get information from page%d in %s"%(page_num,self.url))
        end = False
        
        response = requests.get(url,headers=self.headers)
        response.encoding = response.apparent_encoding
        soup = bs(response.text,features="html.parser")
        movies = soup.select("ul.pt20>li")
        next=soup.select("li.next>a")[0].get('class')
        if next == ["off"]:
            end = True 
        if page_num>=3:
            end = True
        
        for  movie in movies:
            tmp=self.get_movie_dct_from_soup(movie)
            if tmp is None:
                continue
            self.movies_dict[tmp['id']]=tmp
        return end
    
    def get_movie_dct_from_soup(self,movie):
        movie=movie.select('a.js-view-sample')
        if len(movie)==0:
            return None
        else:
            movie = movie[0]
        id=movie.get('data-id')
        preview_url= movie.get('data-video-high')
        actress=movie.get('data-actress')
        product_page_url=movie.get("data-product-page-url")
        poster = movie.get('data-poster')
        title = movie.get('data-title')
        tmp={
            "id":id,
            "actress":actress,
            "preview_url":preview_url,
            "product_page_url":product_page_url,
            "poster":poster,
            "title":title
        }
        return tmp
        
    def  save_movies_dict(self,js,path,file):
        path = os.path.join(path,path)
        if not os.path.exists(path):
            os.mkdir(path)
        file_name = os.path.join(path,file)
        with open(file_name,'w') as f:
            json.dump(js,f)
            print("Json file dump to %s"%(file_name))
            
    def download_all_resources(self):
        if self.flag_complete():
            return
        try:
            if len(self.movies_dict.keys())==0:
                print("Try to load movie dict from json....")
                self.get_all_movies_from_json()
        except Exception as e:
            print("Get movies dict failed! in %s"%self.actress_path,e)
            return
            
        folder=['half','full','preview']
        for f in folder:
            path = os.path.join(self.actress_path,f)
            if not os.path.exists(path):
                os.mkdir(path)
        self.download(self.img,os.path.join(self.actress_path,"actress.jpg"))
        l=len(self.movies_dict)
        if l > 120:
            l=120
        count=1
        for id,movie in self.movies_dict.items():
            if count > l:
                break
            post_small = movie['poster']
            small_name = post_small.split('/')[-1]
            post_large = post_small[:-5]+"l.jpg"
            large_name = post_large.split('/')[-1]
            print("Movies %d/%d : "%(count,l))
            # self.download(post_small,os.path.join(self.actress_path,'half',small_name))
            self.download(post_large,os.path.join(self.actress_path,'full',large_name))
            # self.download(movie['preview_url'],os.path.join(self.actress_path,'preview',self.id+'.mp4'))
            count+=1
        self.flag_complete(set=True)

            
    def flag_complete(self,set=False):
        file_name = os.path.join(self.actress_path,"complete.json")
        if set:
            with open(file_name,'w') as f:
                json.dump(self.movies_dict,f)
                print("Downloading Completed of %s"%self.en_name)
                return True
        else:
            if os.path.exists(file_name):
                print("Actress %s is Exists."%self.en_name)
                return True
            return False

                        
    def get_all_movies_from_json(self):
        
        file_name = os.path.join(self.actress_path,self.en_name+".json")
        if os.path.exists(file_name):
            try:
                print("Try get movies from json file.")
                with  open(file_name,'r') as f:
                    self.movies_dict=json.load(f)
                    return 
            except Exception as e:
                print("Load file Failed %s with error: "%file_name,e)
        
        print("Try to download all movie informations of %s:..."%self.en_name)
        self.get_all_movies()
        

    def download(self,url,file_name):
        
            
        if os.path.exists(file_name):
            print("%s is exist."%file_name)
            return
        print("Downloading %s to %s. (after %d times will have a break. )"%(file_name,self.actress_path,self.download_count))
        self.download_count-=1
        if self.download_count==0:
            self.download_count=60
            print("休息一下，马上回来")
            time.sleep(self.sleep_time)
        try_times=3
        while try_times!=0:
            try_times-=1
            try:
                down_res=requests.get(url,headers=self.headers)
                break
            except Exception as e:
                print("Downloading Faild with error: ",e)
                time.sleep(60)
        try:
            with  open(file_name,'wb') as f:
                f.write(down_res.content)
        except Exception as e:
            print("Downloading %s Failed with Error: ",e)
        
        
        
        
        
if __name__ == '__main__':
    a=ActressManager()
    res = a.get_actress_from_json(1)
    a.download_actresses_in_list(res)
    # a.update_all()
#     dct={
#     "url": "https://www.r18.com/videos/vod/movies/list/?id=27230&type=actress",
#     "img": "https://pics.r18.com/mono/actjpgs/tanaka_hitomi3.jpg",
#     "name": "Hitomi\n...",
#     "id": "27230",
#     "en_name": "tanaka_hitomi3"
# }
   
    
    # dct = {
    # "url": "https://www.r18.com/videos/vod/movies/list/?id=1008785&type=actress",
    # "img": "https://pics.r18.com/mono/actjpgs/sinoda_yuu.jpg",
    # "name": "Yu\nShinoda",
    # "id": "1008785",
    # "en_name": "sinoda_yuu"
    #     }
    # actr=Actress(dct)
    # actr.download_all_resources()

    
        
        