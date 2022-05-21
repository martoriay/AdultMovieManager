import sys,os
from tkinter import *
import tkinter as tk 
import shutil

import sys
import os
sys.path.append(os.path.abspath('./'))

from utils.movie import Movie
from utils.download import download,pic_down

import threading


class MovieName:
    data_fold=[]
    def __init__(self,path):
        self.path=path
        self.failed_file=os.path.join(path,'faied_file.txt')
            
    def mkdir_not_exist(self,path):
        if os.path.exists(path):
            return False
        else:
            return True
            
    def txt_parser(self,path):
        try:
            with open(path,'r') as f:
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
        return fin_res
    
    def make_folds_in_res(self,res):
        failed_list=[]
        
        def check_complete(name):
            if os.path.exists(os.path.join(self.path,name,"complete.json")):
                return True
            else:
                return False
        
        fold=['video','detail','preview','related','actress']
        
        # class myTread(threading.Thread):
        #     def __init__(self,data):
        #         threading.Thread.__init__(self)
        #         self.data=data
        #     def run(self):
                
            
        for r in res:
            path=self.path+"/"+r
            flag=self.mkdir_not_exist(path)
            if flag==False:
                if check_complete(r):
                    print("%s is Downloaded."%r)
                    continue
            
            movie=Movie(r)

            d,info=movie.detail_parser(test_file=None)
            
                 

            
            def down_atr():
                for n in d['nvyoutu']:
                    download(n,os.path.join(path,'actress'))
                download(d['fengmian'],os.path.join(path,'detail'))
            
            def down_xx():
                # for n in d['xiangxi']:
                #     download(n,os.path.join(path,'detail'))
                pic_down(d['xiangxi'],os.path.join(path,'detail'))
                    
            def down_rel():
                # for n in d['related']:
                    # download(n,os.path.join(path,'related'))
                pic_down(d['related'],os.path.join(path,'related'))
                    
            def down_mp4():
                download(d['mp4'],os.path.join(path,'preview'))
                
            
            
            if d==None:
                print("%s 获取信息失败，请重新尝试"%r)
                failed_list.append(r+'\n')
                continue
            try:
                os.mkdir(path)
                for f in fold:
                    os.mkdir(os.path.join(path,f))   
                    
                thrd_atr=threading.Thread(target=down_atr)
                thrd_xx=threading.Thread(target=down_xx)           
                thrd_rel=threading.Thread(target=down_rel)
                thrd_mp4=threading.Thread(target=down_mp4)
                
                thrd_atr.start()
                thrd_xx.start()
                thrd_mp4.start()
                thrd_rel.start()
                
                thrd_atr.join()
                thrd_xx.join()
                thrd_mp4.join()
                thrd_rel.join()
                
                movie.save_info(info,os.path.join(path,'complete.json'))
                print("%s 下载完成"%r)
                
            except Exception as e:
                print("Error:",e)
            if len(failed_list)>0:
                with open(self.failed_file,'w') as f:
                    f.writelines(failed_list)
                print("失败文件已经记录，请查询。")
        
    def down_movie(self,movie,down_path):
        origin_id=movie.origin_id.upper()
        if os.path.exists(os.path.join(down_path,origin_id,'complete.json')):
            print("Movie %s exists."%origin_id)
            return
        
        path=os.path.join(down_path,origin_id)
        
        fold=['video','detail','preview','related','actress']
        d,info=movie.detail_parser(test_file=None)
            
        # def down_atr():
        #     for n in d['nvyoutu']:
        #         download(n,os.path.join(path,'actress'))
        #     download(d['fengmian'],os.path.join(path,'detail'))
        
        # def down_xx():
        #     for n in d['xiangxi']:
        #         download(n,os.path.join(path,'detail'))
                
        # def down_rel():
        #     for n in d['related']:
        #         download(n,os.path.join(path,'related'))
                
        # def down_mp4():
        #     if d['mp4']!=None:
        #         download(d['mp4'],os.path.join(path,'preview'))
            
        # print("come here")
        
        def down_atr():
                for n in d['nvyoutu']:
                    download(n,os.path.join(path,'actress'))
                download(d['fengmian'],os.path.join(path,'detail'))
            
        def down_xx():
            for n in d['xiangxi']:
                download(n,os.path.join(path,'detail'))
            # pic_down(d['xiangxi'],os.path.join(path,'detail'))
                
        def down_rel():
            for n in d['related']:
                download(n,os.path.join(path,'related'))
            # pic_down(d['related'],os.path.join(path,'related'))
                
        def down_mp4():
            download(d['mp4'],os.path.join(path,'preview'))
        
        
        if d==None:
            print("%s 获取信息失败，请重新尝试"%origin_id)
            return
        
        try:
            os.mkdir(path)
            print("Path:",path)
            for f in fold:
                os.mkdir(os.path.join(path,f)) 
            print("path=%s"%os.path.join(path,f))
            thrd_atr=threading.Thread(target=down_atr)
            thrd_xx=threading.Thread(target=down_xx)           
            thrd_rel=threading.Thread(target=down_rel)
            thrd_mp4=threading.Thread(target=down_mp4)
            
            thrd_atr.start()
            thrd_xx.start()
            thrd_mp4.start()
            thrd_rel.start()
            
            thrd_atr.join()
            thrd_xx.join()
            thrd_mp4.join()
            thrd_rel.join()
            
            movie.save_info(info,os.path.join(path,'complete.json'))
            print("%s 下载完成"%movie.origin_id)
            
        except Exception as e:
            print("Error:",e)

    def clear_failed_fold(self):
        fold_list = os.listdir(self.path)
        for fl in fold_list:
            if os.path.isdir(os.path.join(self.path,fl)):
                if os.path.exists(os.path.join(self.path,fl,'complete.json')):
                    pass
                else:
                    shutil.rmtree(os.path.join(self.path,fl))
                    print("Empty %s is deleted!"%fl)
                    
            
    def run(self,file_name="movies.txt"):
        res=self.txt_parser(os.path.join(self.path,file_name))
        self.make_folds_in_res(res)

if __name__ == "__main__":
    m=MovieName("/Volumes/Movie/Manager")
    m.run()
    m.clear_failed_fold()
    
    
    
            