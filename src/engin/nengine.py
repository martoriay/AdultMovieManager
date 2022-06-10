# -*- encoding: utf-8 -*-
'''
@File    :   nengine.py
@Time    :   2022/06/08 23:45:53
@Author  :   Muyao ZHONG 
@Version :   1.0
@Contact :   zmy125616515@hotmail.com
@License :   (C)Copyright 2019-2020
@Title   :   New Engine
'''


from functools import partial
import json
import sys
import os
from urllib.parse import urlencode

sys.path.append(os.path.abspath('./'))

from database.db import Engin, EngineDB
from engin.attr import Attr
import requests
from bs4 import BeautifulSoup as bs 
import threading
import platform
from rule import Ruler
import tkinter as tk
from tkinter import *
from tkinter import ttk 
from utils.common import ui_clean,get_soup

class Engine:
    manager_path="/Volumes/Movie"
    def __init__(self,name="",url="",levels=['category','collection','picture']):
        self.engine_url=url
        self.engine_name=name
        self.item=name+"_item"
        
        self.levels=levels
        self.rules=[None for _ in range(len(self.levels))]
        self.level_index=0
        self.test_soup=None
        self.test_url=""
        self.category=[]
        self.path=os.path.join(self.manager_path,self.engine_name)
        
    def engine_create_ui(self,rroot=None):
        if rroot==None:
            self.root=tk.Tk()
            self.root.title(self.engine_name)
            self.root.geometry('640x480')
        else:
            self.root=rroot
            
        Label(self.root,text="开始获取:"+self.levels[self.level_index]).pack()
        test_frm=Frame(self.root)
        
        self.test_ui(rroot=test_frm,name=self.levels[self.level_index])
        
        def next_level_test():
            self.level_index+=1
            if self.level_index<len(self.levels):
                self.test_ui(rroot=test_frm,name=self.levels[self.level_index])
            else:
                self.start_ui()
        Button(self.root,text="下一层级测试",command=next_level_test).pack()
        
        if rroot==None:
            self.root.mainloop()
        
    def test_ui(self,rroot=None,name=""):
        # 清空用于临时存储的属性
        self.tmp_attr=[]
        
        if rroot==None:
            root=tk.Tk()
            root.title(name)
            root.geometry('640x480')
        else:
            root=rroot
            ui_clean(root)
            
        test_frm=Frame(root)
        test_frm.pack()
        
        row=0
        # Label(test_frm,text=name).grid(row=row,column=0)
        row+=1
        Label(test_frm,text="网址： ").grid(row=row,column=0)
        url_entry=Entry(test_frm,textvariable=StringVar(value="https://www.xinmeitulu.com"))
        url_entry.grid(row=row,column=1)

        row+=1
        Label(test_frm,text="选择器： ").grid(row=row,column=0)
        selector_entry=Entry(test_frm,textvariable=StringVar(value='#menu-main>li>a'))
        selector_entry.grid(row=row,column=1)
        
        row+=1
        Label(test_frm,text="属性： ").grid(row=row,column=0)
        attr_entry=Entry(test_frm,textvariable=StringVar(value='href'))
        attr_entry.grid(row=row,column=1)
        
        # def need_check():
        # Button(root,text="需要验证",command=partial(need_check)).grid(row=row,column=0)
        
        row+=1
        Label(test_frm,text="验证值属性： ").grid(row=row,column=0)
        check_attr_entry=Entry(test_frm,textvariable=StringVar(value=''))
        check_attr_entry.grid(row=row,column=1)
        
        row+=1
        Label(test_frm,text="验证值： ").grid(row=row,column=0)
        check_value_entry=Entry(test_frm,textvariable=StringVar(value=''))
        check_value_entry.grid(row=row,column=1)
        
        row+=1
        result=Text(test_frm,height=10,width=50)
        result.grid(row=row,column=0,columnspan=2)
        
        def init_soup():
            url=url_entry.get()
            if not self.test_soup:
                self.test_soup=get_soup(url)
                self.test_url=url
            else:
                if url!=self.test_url:
                    self.test_url=url
                    self.test_soup=get_soup(url)
                    
        #! 开始测试  
        def start_test():
            init_soup()

            selector=selector_entry.get()
            attr=attr_entry.get()
            
            # check_selector=check_selector_entry.get()
            check_attr=check_attr_entry.get()
            check_value=check_value_entry.get()
            elements=self.test_soup.select(selector)
            
            res=[]
            
            if check_attr=="" or check_attr=='输入验证值属性':
                for e in elements:
                    if attr=="":
                        res.append(e)
                        break
                    
                    if attr=='text':
                        res.append(e.get_text())
                    else:
                        res.append(e.get(attr))
            else:
                for e in elements:
                    if check_attr=="text":
                        cv=e.get_text()
                    else:
                        cv=e.get(check_attr)
                    
                    if cv == check_value:
                        if attr=='text':
                            res.append(e.get_text())
                        else:
                            res.append(e.get(attr))
            
            # 将获得的结果插入到文本域中                
            output=""
            for r in res:
                output+=str(r)+'\n'
            result.insert(INSERT,output)
            
            
        #! 提取规则
        def get_rule():

            selector=selector_entry.get()
            attr=attr_entry.get()
            
            # check_selector=check_selector_entry.get()
            check_attr=check_attr_entry.get()
            check_value=check_value_entry.get()
            
            attrs=[]
            for a in self.tmp_attr:
                attrs.append(a.get())
                
            rule=Ruler.make_rule(name,selector,attr,check_attr,check_value,attrs)
            self.rules[self.level_index]=rule
            print(self.rules)
            
            #TODO ： 对于第一层不再产生规则，而是将信息保存在对象中
            # if self.level_index==0:
            #     init_soup()
            #     res=[]
            
            return rule
            
        row+=1
        attr_frm=Frame(root)
        attr_frm.pack()

        def add_attr():
            init_soup()
            selector=selector_entry.get()
            
            s=self.test_soup.select(selector)[0]
            a=Attr(soup=s)
            a.attr_ui(attr_frm)
            self.tmp_attr.append(a)
                
            
        def delete_attr():
            if len(self.tmp_attr)>0:
                a=self.tmp_attr.pop(-1)
                a.destroy_ui()
            
        last_button=Frame(root)
        last_button.pack()
        row=0
        Button(last_button,text='添加属性',command=add_attr).grid(row=row,column=0)
        Button(last_button,text='删除属性',command=delete_attr).grid(row=row,column=1)
        row+=1
        Button(last_button,text="开始测试",command=start_test).grid(row=row,column=0)
        Button(last_button,text="保存结果",command=get_rule).grid(row=row,column=1)
        
        if rroot==None:
            test_frm.mainloop()
        else:
            root.pack()
            
    def start_ui(self,root=None):
        if root==None:
            start=tk.Tk()
            start.geometry('640x480')
            start.title('准备下载')
        else:
            start=root
        info=Frame(start)
        info.pack()
        row=0
        Label(info,text="输入引擎名字：").grid(row=row,column=0)
        name_entry=Entry(info,textvariable=StringVar(value=self.engine_name))
        name_entry.grid(row=row,column=1)
        
        row+=1
        Label(info,text="网站地址:").grid(row=row,column=0)
        url_entry=Entry(info,textvariable=StringVar(value=self.engine_url))
        url_entry.grid(row=row,column=1)
        
        def build_db():
            self.engine_name=name_entry.get()
            self.engine_url=url_entry.get()
            db=EngineDB()
            db.build_db(self)
            
        def save_to_file():
            self.engine_name=name_entry.get()
            self.url=url_entry.get()
            
            dct={
                'name':self.engine_name,
                'url':self.engine_url,
                'rules':self.rules,
                'category':self.category,
                'levels':self.levels
            }
            with open('engin/engines.json','r') as f:
                exist=json.load(f)
                exist[self.engine_name]=dct
                
            with open('engin/engines.json','w') as f:
                json.dump(exist,f)
                print("引擎信息已经写入")

        Button(start,text='建立数据库',command=build_db).pack()
        Button(start,text='保存引擎',command=save_to_file).pack()
        
        for i in range(len(self.levels)):
            f=Frame(start)
            Button(f,text="开始爬取"+self.levels[i],command=print).grid(row=0,column=0)
            Button(f,text="多线程爬取",command=print).grid(row=0,column=1)
            f.pack()
            
    
            
            
class EngineManager:
    engine_file='engin/engines.json'
    def __init__(self):
        self.root=Tk()
        self.root.geometry('640x480')
        self.root.title('引擎选择')
    
    def engine_select(self):
        with open(self.engine_file,'r') as f:
            exists=json.load(f)
        
        Button(self.root,text="新建空白引擎",command=self.new_engine).pack()
        
        for name,e in exists.items():
            Button(self.root,text="打开引擎"+name,command=partial(self.open_engine,e)).pack()
        
    def new_engine(self):
        engine=Engine(levels=['category','collection','item'])
        engine.engine_create_ui()
        
    def open_engine(self,e):
        engine=Engine(name=e['name'],url=e['url'],levels=e['levels'])
        engine.engine_create_ui()
        
    def run(self):
        self.engine_select()
        self.root.mainloop()
        
if __name__ == '__main__':
    em=EngineManager()
    em.run()
    