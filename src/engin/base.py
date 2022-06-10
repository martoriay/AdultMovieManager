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

import sys
import os

sys.path.append(os.path.abspath('./'))
import requests
from bs4 import BeautifulSoup as bs 
import threading
import platform

class Engin:
    pltfm=platform.platform()
    version = "1.0.0"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15',
        }
    manager_path = "/Volumes/Movie"
    def __init__(self,base_url,engin_name=""):
        if self.pltfm[0]=='m':
            self.manager_path = "/Volumes/Movie"
        elif self.pltfm[0]=='w':
            self.manager_path = 'Z:'
        if engin_name!="":
            self.engin_path=os.path.join(self.manager_path,engin_name)
        else:
            self.engin_path=self.manager_path
        if not os.path.exists(self.engin_path):
            os.mkdir(self.engin_path)
        self.engin_name=engin_name
        self.base_url=base_url
        self.detail_url=""
        self.search_url=""
        self.pages_url=[]
        
    def get_soup(self,url,debug=False):
        html=requests.get(url,headers=self.headers)
        if debug:
            print("Response:",html.status_code)
        html.encoding = html.apparent_encoding
        soup = bs(html.text,features="html.parser")
        return soup
    
    def get_content_from_url(self,url,selector):
        soup=self.get_soup(url)
        content = soup.select(selector)
        return content
    
    def get_content_from_soup(self,soup,selector):
        return soup.select(selector)
    
    def download_single(self,url,path,name=""):
        if name == "":
            file_name = url.split('/')[-1]
        else:
            file_name = name
        file_name = os.path.join(path,file_name)
        if os.path.exists(file_name):
            print("%s is exists."%file_name)
        else:
            down_res = requests.get(url,headers=self.headers)
            try:
                with open(file_name,'wb') as f:
                    f.write(down_res.content)
                print("%s downloaded."%file_name)
            except Exception as e:
                print("Download Single FIle %s Error:"%file_name,e)
                
    def parse_url_to_pre_and_file(self,url):
        url_s=url.split('/')
        file_name=url_s[-1]
        url_pre=""
        for i in range(len(url_s)-1):
            url_pre+=url_s[i]
            url_pre+='/'
        return url_pre,file_name
    
    def update_database(self,dct):
        pass
    
    def get_content_list(self,url,selector,next=True):
        if not next:
            return
        soup=self.get_soup(url)

        
        
        
    

            

        
if __name__ == '__main__':
    e=Engin('hht')
                
