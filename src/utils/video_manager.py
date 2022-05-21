# -*- encoding: utf-8 -*-
'''
@File    :   video_manager.py
@Time    :   2022/05/13 01:18:48
@Author  :   Muyao ZHONG 
@Version :   1.0
@Contact :   zmy125616515@hotmail.com
@License :   (C)Copyright 2019-2020
@Title   :   Video Manager
'''


import sys
import os

sys.path.append(os.path.abspath('./'))

import shutil,re

class Manager:
    def __init__(self,origin_path,target_path):
        self.origin_path=origin_path
        self.target_path=target_path
        self.mp4_files=[]
        
    def iter_dir(self,old_path):
        # print("正在搜索文件夹：%s"%old_path)
        dir_list=os.listdir(old_path)
        for d in dir_list:
            new_path=os.path.join(old_path,d)
            # print(new_path)
            if os.path.isdir(new_path):
                self.iter_dir(new_path)
            elif os.path.isfile(new_path) and os.path.getsize(new_path)/(2**30)>1:
                if new_path.endswith('.mp4'):
                    self.mp4_files.append(new_path+'\n')
                else:
                    pass
        
    def search_file(self):
        self.iter_dir(self.origin_path)
        with open(os.path.join(self.target_path,"all_mp4.txt"),'w') as f:
            f.writelines(self.mp4_files)
        print("Mp4 文件路径已经保存。")
        
    def parse_file_name(self,file_path,out_file_path):
        with open(file_path,'r') as f:
            files=f.readlines()
            print(files)
        dct=[]
        manual_dct=[]
        for path in files:
            try:
                # print(path)
                file_path,file_name_ext=os.path.split(path)
                file_name,file_ext=file_name_ext.split('.')
                pattern='[a-zA-Z]{3,5}-[0-9]{3,5}'
                match=re.search(pattern,file_name)
                if match:
                    id=file_name[match.start():match.end()]
                    print("ID %s found in %s"%(id,path))
                    dct.append(path[:-1]+'  '+id+'\n')
                else:
                    manual_dct.append(path+"\n")
            except Exception as e:
                manual_dct.append(path+'\n')
                print("Error:",e)
                
        count=1
        l=len(manual_dct)
        for path in manual_dct:
            x=input("(%d/%d)输入%s的ID"%(count,l,path))
            count+=1
            if x=="":              
                continue
            else:
                dct.append(path[:-1]+"  "+x+"\n")
                
            
            
        with open(out_file_path,'w') as f:
            f.writelines(dct)
            print("文件已经写入，请查看。%s"%out_file_path)

if __name__ == "__main__":
    m=Manager("/Volumes/Movie/newDownload","/Volumes/Movie/newDownload")
    # m.search_file()
    m.parse_file_name("/Volumes/Movie/newDownload/all_mp4.txt",'/Volumes/Movie/newDownload/out_all_mp4.txt')
                
                    
                