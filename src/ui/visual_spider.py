# -*- encoding: utf-8 -*-
'''
@File    :   visual_spider.py
@Time    :   2022/06/07 02:01:19
@Author  :   Muyao ZHONG 
@Version :   1.0
@Contact :   zmy125616515@hotmail.com
@License :   (C)Copyright 2019-2020
@Title   :   
'''

from functools import partial
import sys
import os
sys.path.append(os.path.abspath('./'))

import tkinter as tk
from tkinter import *
from tkinter import ttk 
from utils.common import get_soup

class Selector:
    def __init__(self,root=None,name="Selector",test_url=""):
        if root==None:
            self.root=tk.Tk()
            self.root.geometry('480x320')
        else:
            self.root=root
        self.test_url=test_url
        self.name=name
        Label(self.root,text=self.name).pack()
        Label(self.root,text="输入选择器：")
        self.selector=Entry(self.root,textvariable=StringVar(value='.comicpage>div>img'))
        self.selector.pack()
        Label(self.root,text="输入属性名：")
        self.attr_name=Entry(self.root,textvariable=StringVar(value='data-original'))
        self.attr_name.pack()
        Label(self.root,text="输入测试方式：")
        self.check_attr=Entry(self.root,textvariable=StringVar(value="输入测试属性"))
        self.check_value=Entry(self.root,textvariable=StringVar(value="输入测试属性值"))
        self.check_attr.pack()
        self.check_value.pack()
        Button(self.root,text="测试选择器",command=self.get).pack()
        self.test_output=Text(self.root,height=10,width=30)
        self.test_output.pack()
        
        
    def get(self):
        soup=get_soup(self.test_url)
        selector=self.selector.get()
        lst=soup.select(selector)
        attr=self.attr_name.get()
        res=""
        check=False
        if self.check_value=="输入测试属性值" or self.check_value=='':
                pass
        else:
            check=True
            check_attr=self.check_attr.get()
            check_value=self.check_value.get()
            
        for l in lst:
            if check:
                ta=l.get(check_attr)
                if check_value!=ta:
                    continue
            url=l.get(attr)
            print(url)
            res+=url+"\n"
        print(res)
        self.test_output.insert(INSERT,res)
        
class NextPage:
    def __init__(self,root=None,name="NextPage",test_url=""):
        if root==None:
            self.root=tk.Tk()
            self.root.geometry('480x320')
        else:
            self.root=root
        self.test_url=test_url
        self.name=name
        Label(self.root,text=self.name).pack()
        Label(self.root,text="输入选择器：")
        self.selector=Entry(self.root,textvariable=StringVar(value='.fanye'))
        self.selector.pack()
        Label(self.root,text="输入属性名：")
        self.attr_name=Entry(self.root,textvariable=StringVar(value='href'))
        self.attr_name.pack()
        Label(self.root,text="输入测试方式：")
        self.check_attr=Entry(self.root,textvariable=StringVar(value="输入测试属性"))
        self.check_value=Entry(self.root,textvariable=StringVar(value="输入测试属性值"))
        self.check_attr.pack()
        self.check_value.pack()
        Button(self.root,text="测试选择器",command=self.get).pack()
        self.test_output=Text(self.root,height=10,width=30)
        self.test_output.pack()
        
        
    def get(self):
        soup=get_soup(self.test_url)
        selector=self.selector.get()
        lst=soup.select(selector)
        attr=self.attr_name.get()
        test_attr=self.check_attr.get()
        test_value=self.check_value.get()
        res="没找到下一页"
        for l in lst:
            tmp=l.get(attr)
            if test_attr=="输入测试属性" or test_attr=='':
                ta=l.get_text()
            else:
                ta=l.get(test_attr)
            if ta==test_value:
                res=tmp 
                break 
        
        print(res)
        self.test_output.insert(INSERT,res+'\n')
        return res
    
class AttrSelect:
    def __init__(self,root=None,name="Attr Page",test_url="",util="fold_name"):
        if root==None:
            self.root=tk.Tk()
            self.root.geometry('480x320')
        else:
            self.root=root
        
        self.test_url=test_url
        self.name=name
        Label(self.root,text=self.name).pack()
        Label(self.root,text="输入属性用途：")
        self.attr_util=Entry(self.root,textvariable=StringVar(value=util))
        self.attr_util.pack()
        Label(self.root,text="输入选择器：")
        self.selector=Entry(self.root,textvariable=StringVar(value='.fanye'))
        self.selector.pack()
        Label(self.root,text="输入属性名：")
        self.attr_name=Entry(self.root,textvariable=StringVar(value='href'))
        self.attr_name.pack()
        Label(self.root,text="输入测试方式：")
        self.check_attr=Entry(self.root,textvariable=StringVar(value="输入测试属性"))
        self.check_value=Entry(self.root,textvariable=StringVar(value="输入测试属性值"))
        self.check_attr.pack()
        self.check_value.pack()
        Button(self.root,text="测试选择器",command=self.get).pack()
        self.test_output=Text(self.root,height=10,width=30)
        self.test_output.pack()
        
    def get(self):
        soup=get_soup(self.test_url)
        selector=self.selector.get()
        lst=soup.select(selector)
        attr=self.attr_name.get()
        test_attr=self.check_attr.get()
        test_value=self.check_value.get()
        res="没找到下一页"
        for l in lst:
            tmp=l.get(attr)
            if test_attr=="输入测试属性" or test_attr=='':
                ta=l.get_text()
            else:
                ta=l.get(test_attr)
            if ta==test_value:
                res=tmp 
                break 
        
        print(res)
        self.test_output.insert(INSERT,res+'\n')
        return res
            

class VisualSpider:
    def __init__(self,root=None):
        if root==None:
            self.root=tk.Tk()
            self.root.geometry('1920x1080')
        else:
            self.root=root
        self.note=ttk.Notebook(self.root)

    def level0_note(self):
        l0=Frame(self.note)
        test_url_frm=Frame(l0)
        Label(test_url_frm,text="测试链接：").pack(side=LEFT)
        self.test_url=Entry(test_url_frm,textvariable=StringVar(value="https://www.xinmeitulu.com/photo/田中まな《新世紀エヴァンゲリオン》綾波レイ-cosplay-c"),width=100)
        self.test_url.pack(side=LEFT)
        test_frm=Frame(l0)
        Button(test_url_frm,text="刷新测试链接",command=partial(self.update_test_url,test_frm)).pack(side=LEFT)
        test_url_frm.pack()
        test_frm.pack()
        self.note.add(l0,text="Level0")
        
    
    def update_test_url(self,l0):
        for c in l0.winfo_children():
            c.pack_forget()
        
        ##? 图片列表选择器测试
        list_rule_frm=Frame(l0)
        Label(list_rule_frm,text="输入获取图片的方式").pack()
        rule_frm=Frame(list_rule_frm)
        test_url=self.test_url.get()
        self.pic_selector=Selector(rule_frm,"图片选择器",test_url)
        rule_frm.pack()
        list_rule_frm.pack(side=LEFT)
        
        ##? 属性选择器
        attr_rule_frm=Frame(l0)
        Label(attr_rule_frm,text="属性选择器").pack(side=LEFT)
        Button(attr_rule_frm,text="添加属性选择",command=(print,("hello,world",))).pack()
        attr_frm=Frame(attr_rule_frm)
        self.fold_name=AttrSelect(attr_frm,name="文件路径",util="fold_name")
        attr_frm.pack()
        attr_rule_frm.pack(side=LEFT)
        
        ##? 下页选择器
        next_page_frm=Frame(l0)
        Label(next_page_frm,text="输入下页判断方式").pack()
        page_frm=Frame(next_page_frm)
        self.next_page_selector=NextPage(page_frm,name="下页选择器",test_url=test_url)
        page_frm.pack()
        next_page_frm.pack()
        
 
        
        
            
    def run(self):
        
        self.level0_note()
        self.note.pack()
        self.root.mainloop()
            

        
        
if __name__ == '__main__':
    v=VisualSpider()
    v.run()