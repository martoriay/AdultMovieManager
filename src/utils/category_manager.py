# -*- encoding: utf-8 -*-
'''
@File    :   manager_category.py
@Time    :   2022/05/17 19:53:30
@Author  :   Muyao ZHONG 
@Version :   1.0
@Contact :   zmy125616515@hotmail.com
@License :   (C)Copyright 2019-2020
@Title   :   categoryes Manager

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

class CategoryManager:
    manager_path = "/Volumes/Movie/Manager/Categories"
    url= "https://www.r18.com/videos/vod/movies/category/?lg=zh"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
    }
    
    def __init__(self):
        self.categories_keys=["situation","type","costume","genre","play","other"]
        self.categories={
            key:[] for key in self.categories_keys
        }
        if not os.path.exists(self.manager_path):
            os.mkdir(self.manager_path)
        self.file_path = os.path.join(self.manager_path,"all_category.json")
        
    
    def get_all_categoris(self):
        response = requests.get(self.url,headers=self.headers)
        response.encoding = response.apparent_encoding
        soup = bs(response.text,features="html.parser")
        categories = soup.select("#contents>ul")[1:]
        for i in range(len(self.categories_keys)):
            category=categories[i]
            key=self.categories_keys[i]
            tmp=category.select("li>a")
            for a in tmp:
                title=a.text
                href=a.get('href')
                self.categories[key].append(
                    {
                        "title":title,
                        "href":href
                    }
                )
        try:
            with open(self.file_path,'w') as f:
                json.dump(self.categories,f)
        except Exception as e:
            print("Save CateInfo failed %s:Error"%self.file_path,e)
            
        
    def load_categories_info(self):
        if os.path.exists(self.file_path):
            with open(self.file_path,'r') as f:
                self.categories = json.load(f)
        else:
            self.get_all_categoris()
            
    def download_all_categories_info(self):
        self.load_categories_info()
        for key in self.categories_keys:
            categories = self.categories[key]
            
            for category in categories:
                cate = Category(category)
                cate.get_all_movies_from_json()
                cate.download_all_resources()
                           
class Category:
    category_path="/Volumes/Movie/Manager/Categories"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
    }
    download_count = 60
    sleep_time = 60
    
    def __init__(self,dct):
        # self.url = dct['url']
        # self.img = dct['img']
        # self.name = dct['name']
        # self.en_name = dct['en_name']
        # self.id = dct['id']
        self.movies_dict={}
        self.title = dct['title']
        self.url = dct['href']
        self.category_path=os.path.join(self.category_path,self.title)
        
    def get_all_movies(self):
        if not os.path.exists(self.category_path):
            os.mkdir(self.category_path)
        page_num=1
        flag=False
        while not flag:
            flag=self.get_movies_from_page(page_num)
            # self.save_movies_dict(self.movies_dict,self.category_path,self.en_name+'.json')
            page_num+=1
            # break
        self.save_movies_dict(self.movies_dict,self.category_path,self.title+'.json')
        return
            
        
    def get_movies_from_page(self,page_num):
        url = self.url+"&page="+str(page_num)+"&lg=zh"
        print("Get information from page-%d in %s"%(page_num,self.url))
        end = False
        
        response = requests.get(url,headers=self.headers)
        response.encoding = response.apparent_encoding
        soup = bs(response.text,features="html.parser")
        
        movies = soup.select("ul.pt20>li")
        next=soup.select("li.next>a")[0].get('class')
        
        if next == ["off"]:
            end = True 
        if page_num>=10:
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
        category=movie.get('data-category')
        product_page_url=movie.get("data-product-page-url")
        poster = movie.get('data-poster')
        title = movie.get('data-title')
        tmp={
            "id":id,
            "category":category,
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
            print("Get movies dict failed! in %s"%self.category_path,e)
            return
            
        folder=['half','full','preview']
        for f in folder:
            path = os.path.join(self.category_path,f)
            if not os.path.exists(path):
                os.mkdir(path)
        # self.download(self.img,os.path.join(self.category_path,"category.jpg"))
        l=len(self.movies_dict)
        if l > 300:
            l=300
        count=1
        for id,movie in self.movies_dict.items():
            if count > l:
                break
            post_small = movie['poster']
            small_name = post_small.split('/')[-1]
            post_large = post_small[:-5]+"l.jpg"
            large_name = post_large.split('/')[-1]
            print("Movies %d/%d : "%(count,l))
            # self.download(post_small,os.path.join(self.category_path,'half',small_name))
            self.download(post_large,os.path.join(self.category_path,'full',large_name))
            # self.download(movie['preview_url'],os.path.join(self.category_path,'preview',self.id+'.mp4'))
            count+=1
        self.flag_complete(set=True)

            
    def flag_complete(self,set=False):
        file_name = os.path.join(self.category_path,"complete.json")
        if set:
            with open(file_name,'w') as f:
                json.dump(self.movies_dict,f)
                print("Downloading Completed of %s"%self.title)
                return True
        else:
            if os.path.exists(file_name):
                print("category %s is Exists."%self.title)
                return True
            return False

                        
    def get_all_movies_from_json(self):
        
        file_name = os.path.join(self.category_path,self.title+".json")
        if os.path.exists(file_name):
            try:
                print("Try get movies from json file.")
                with  open(file_name,'r') as f:
                    self.movies_dict=json.load(f)
                    return 
            except Exception as e:
                print("Load file Failed %s with error: "%file_name,e)
        
        print("Try to download all movie informations of %s:..."%self.title)
        self.get_all_movies()
        

    def download(self,url,file_name):
        if os.path.exists(file_name):
            print("%s is exist."%file_name)
            return
        print("Downloading %s to %s. (after %d times will have a break. )"%(file_name,self.category_path,self.download_count))
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
                time.sleep(600)
        try:
            with  open(file_name,'wb') as f:
                f.write(down_res.content)
        except Exception as e:
            print("Downloading %s Failed with Error: ",e)
            
if __name__ == '__main__':
    c=CategoryManager()
    c.download_all_categories_info()
    
            
            
                
        
