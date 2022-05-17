# -*- encoding: utf-8 -*-
'''
@File    :   movie.py
@Time    :   2022/05/12 17:57:26
@Author  :   Muyao ZHONG 
@Version :   1.0
@Contact :   zmy125616515@hotmail.com
@License :   (C)Copyright 2019-2020
@Title   :   获取电影详情
'''

import requests,json,os,sys
from bs4 import BeautifulSoup as bs 

class Movie:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15',
        "Accept-Language": "zh-CN,zh-Hans;q=0.9"
    }   
    
    requests_url=["https://www.r18.com/api/v4f/contents/%s?lang=zh&unit=USD", # 详情
                  "https://www.r18.com/api/v4f/user/related?content_id=%s&lang=zh&unit=USD",  # 相关
                  #TODO: 登陆相关
                  "https://www.r18.com/api/v4f/user/recommend?content_id=%s&lang=zh&unit=USD", # 推荐
                  #TODO: 演员相关
                  "https://www.r18.com/api/v4f/content/list/actress?actresses[]=%s&lang=zh&unit=USD" # 演员id
                  ]
    
    def __init__(self,id):
        self.origin_id=id
        self.actress=""
        id=id.lower()
        if '-' in id:
            self.id=id.replace('-','00')
        self.id_parser()
        self.content_url = [self.requests_url[0]%self.id,self.requests_url[1]%self.id,self.requests_url[2]%self.id]
        
    def local_info(self,file_path):
        if not os.path.exists(os.path.join(file_path,'detail.json')):
            detail=self.download('detail',file_path)
            try:
                self.actress=detail['actresses'][0]['id']
            except Exception as e:
                print("Actress is None.")
        if not os.path.exists(os.path.join(file_path,'related.json')):
            related=self.download('related',file_path)
        if not os.path.exists(os.path.join(file_path,'actress.json')) and self.actress!="":
            actress=self.download('actress',file_path)
            
        return detail,related,actress
    
    def download(self,flag='detail.json',file_path='./'):
        if flag=='detail.json':
            url=self.requests_url[0]%self.id
        elif flag=='related.json':
            url=self.requests_url[1]%self.id
        elif flag=='actress.json':
            url=self.requests_url[3]%self.actress
        
        try:
            html=requests.get(url,headers=self.headers)
            html.encoding=html.apparent_encoding
            js=html.json()
            with open(os.path.join(file_path,flag),'w') as f:
                json.dump(js,f)
                print("%s %s downloaded in to %s"%(self.origin_id,flag,file_path))
            return js
        except Exception as e:
            print("Down load %s Error:"%flag,e)
            return None
            
    def id_parser(self):
        if self.id.startswith('dfe'):
            self.id='2'+self.id
        elif self.id.startswith('jukf'):
            self.id='h_227'+self.id
        elif self.id.startswith('milk'):
            self.id='h_1240'+self.id
        elif self.id.startswith('ddff'):
            self.id='111'+self.id
        elif self.id.startswith('fsdss'):
            self.id='1'+self.id
        elif self.id.startswith('dv'):
            self.id='53'+self.id
        elif self.id.startswith('sdde'):
            self.id='1'+self.id
        elif self.id.startswith('ienfh'):
            self.id='2'+self.id
        elif self.id.startswith('hodv'):
            self.id='5642hodv'+self.id[-5:]
        elif self.id.startswith('pih'):
            self.id='1'+self.id
        elif self.id.startswith('akdl'):
            self.id='1'+self.id
        elif self.id.startswith('ntr'):
            self.id='1'+self.id

    def get_jsons(self):
        self.jsons=[]
        for i in range(2):
            url=self.content_url[i]
            html=requests.get(url,headers=self.headers)
            html.encoding=html.apparent_encoding
            js=html.json()
            self.jsons.append(js)

        try:
            detail_data=self.jsons[0]['data']
            related_data=self.jsons[1]['data']
            # print(detail_data)
            return detail_data,related_data
        except Exception as e:
            print("Error:",e)
            return None,None
        
    
    def detail_parser(self,test_file='./test_path/test/0.json'):
        flag1=0
        flag2=0
        if test_file!=None:
            with open(test_file,'rb') as f:
                j=json.load(f)['data']
        else:
            detail_data,related_data=self.get_jsons()
            if detail_data==None:
                flag1=1
                # print("详情获取失败")
            if related_data==None:
                flag2=1
                # print("相关获取失败")
            if flag1+flag2>0:
                print("%s 下载失败，请稍后再试"%self.id)
                return None,None
        
        #获取详情
        j=detail_data
        content_id=j['content_id']
        title=j['title']
        release_date=j['release_date']
        runtime=j['runtime_minutes']
        mp4=j['sample']
        if mp4!=None:
            mp4=mp4['high']
        actress=j['actresses'] #一个女优列表，每个元素是一个字典
        if actress==None:
            actress=[]
        
        fengmian=j['images']['jacket_image']['large']
        xiangxi=[i['large'] for i in j['gallery']]
        
        #获取相关信息
        related=[]
        for i in related_data:
            content_id=i['content_id']
            dvd_id=i['dvd_id']
            title=i['title']
            # actress=i['actresses']
            images=i['images']['jacket_image']['large']
            data={
                'title':title,
                "content_id":content_id,
                'dvd_id':dvd_id,
                'fengmian':images
            }  
            related.append(data)
        
        # 组织可下载数据
        try:
            download={
                'nvyoutu':[i['image_url'] for i in actress],
                'fengmian':fengmian,
                'xiangxi':xiangxi,
                'mp4':mp4,
                'related':[d['fengmian'] for d in related]
            }
        except Exception as e:
            print("组织下载数据失败，Error:",e)
            return None,None
        
        # 组织信息数据
        try:
            info={
                'title':title,
                'release_date':release_date,
                'runtime':runtime,
                'content_id':content_id,
                'actress_name':[i['name'] for i in actress],
                'related':[d['dvd_id'] for d in related]
            }
        except Exception as e:
            
            print("组织信息数据失败，Error:",e)
            return None,None
        return download,info
    
    def save_info(self,info,path):
        with open(path,'w') as f:
            json.dump(info,f)
    
    def related_parser(self,test_file="./test_path/test/1.json"):
        if test_file!=None:
            with open(test_file,'rb') as f:
                j=json.load(f)['data']
        else:
            j=self.jsons[1]['data']
        
        res=[]
        for i  in j:
            content_id=i['content_id']
            dvd_id=i['dvd_id']
            title=i['title']
            actress=i['actresses']
            images=i['images']['jacket_image']['large']
            data={
                'title':title,
                "content_id":content_id,
                'dvd_id':dvd_id,
                'fengmian':images
            }
            res.append(data)
        return res
    
class AllMovieInfo:
    def __init__(self,file_path):
        self.file_path=file_path
        self.file=os.path.join(self.file_path,"all_movies.txt")
        self.movies=[]
        
        
    def get_movies(self):
        if not os.path.exists(self.file):
            self.gen_file()
        self.update_movies()
        return self.movies
        
    def update_movies(self):
        self.movies=[]
        try:
            with open(self.file,'r') as f:
                tmp=f.read()
        except Exception as e:
            print("Error:",e)
            sys.exit()
        res=tmp.split('\n')
        fin_res=[]
        for r in res:
            s=r.strip()
            if s!="":
                fin_res.append(s)
        self.movies=fin_res
    
    def gen_file(self):
        movies=[]
        dir_list=os.listdir(self.file_path)
        for d in dir_list:
            if os.path.isdir(os.path.join(self.file_path,d)):
                movies.append(d+'\n')
        try:
            with open(self.file,'w') as f:
                f.writelines(movies)
            print("All movies file generated.")
        except Exception as e:
            print("Write file failed: ",e)
            sys.exit()
 
            
    

if __name__ == "__main__":
    m=AllMovieInfo("/Volumes/Movie/Manager")
    m.get_movies()
    print(m.movies)
    
        
    
        