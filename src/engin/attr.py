# -*- encoding: utf-8 -*-
'''
@File    :   rule.py
@Time    :   2022/06/08 23:46:42
@Author  :   Muyao ZHONG 
@Version :   1.0
@Contact :   zmy125616515@hotmail.com
@License :   (C)Copyright 2019-2020
@Title   :   rules
'''

from abc import abstractmethod
import tkinter as tk
from tkinter import *
from tkinter import ttk


import sys
import os
from tkinter import messagebox
sys.path.append(os.path.abspath('./'))
from utils.common import get_soup 


class Attr:
    def __init__(self,name="",selector="",attr="",check_attr="",check_value="",soup=""):
        self.name=name 
        self.selector=selector
        self.attr=attr 
        self.check_attr=check_attr
        self.check_value=check_value
        self.soup=soup
        
    def attr_ui(self,root=None): 
        if root==None:
            self.root=tk.Tk()
            self.root.title="属性测试"
            self.root.geometry="640x480"
        else:
            self.root=Frame(root)
            
        test_frm=Frame(self.root)
        test_frm.pack()
        row=0
        # Label(test_frm,text=name).grid(row=row,column=0)
        row+=1
        Label(test_frm,text="属性名：").grid(row=row,column=0)
        name_entry=Entry(test_frm,textvariable=StringVar(value=self.name))
        name_entry.grid(row=row,column=1)

        row+=1
        Label(test_frm,text="选择器： ").grid(row=row,column=0)
        selector_entry=Entry(test_frm,textvariable=StringVar(value=self.selector))
        selector_entry.grid(row=row,column=1)
        
        row+=1
        Label(test_frm,text="属性： ").grid(row=row,column=0)
        attr_entry=Entry(test_frm,textvariable=StringVar(value=self.attr))

        attr_entry.grid(row=row,column=1)
        
        
        
        row+=1
        Label(test_frm,text="验证值属性： ").grid(row=row,column=0)
        check_attr_entry=Entry(test_frm,textvariable=StringVar(value=self.check_attr))
        check_attr_entry.grid(row=row,column=1)
        
        row+=1
        Label(test_frm,text="验证值： ").grid(row=row,column=0)
        check_value_entry=Entry(test_frm,textvariable=StringVar(value=self.check_value))
        check_value_entry.grid(row=row,column=1)
        
        row+=1
        result=Text(test_frm,height=3,width=50)
        result.grid(row=row,column=0,columnspan=2)
        
        
        def write_attr():
            self.name=name_entry.get()
            self.selector=selector_entry.get()
            self.attr=attr_entry.get()
            self.check_attr=check_attr_entry.get()
            self.check_value=check_value_entry.get()
            
        def start_test():
            write_attr()
            if self.name=="":
                messagebox.showinfo("提示","没有输入属性名称")
                return 
            if self.selector=="":
                elements=[self.soup]
            else:
                elements=self.soup.select(self.selector)
            res=""
            for e in elements:
                if self.check_attr=="":
                    if self.attr=='text':
                        res=e.get_text()
                    else:
                        res=e.get(self.attr)
                else:
                    if self.check_attr=='text':
                        cv=e.get_text()
                    else:
                        cv=e.get(self.check_attr)
                    if cv==self.check_value:
                        if self.attr=='text':
                            res=e.get_text()
                        else:
                            res=e.get(self.attr)
                    else:
                        res="Check Attr Failed."
                break
            result.insert(INSERT,res)
            print(res)
            
        row+=1
        
        Button(test_frm,text="写入属性列表",command=write_attr).grid(row=row,column=1)
        Button(test_frm,text="测试属性",command=start_test).grid(row=row,column=0)
        
        if root==None:
            self.root.mainloop()
        else:
            self.root.pack()
            
    def get(self):
        res={
            'name':self.name,
            'selector':self.selector,
            'attr':self.attr,
            'check_attr':self.check_attr,
            'check_value':self.check_value
        }
        return res
    
    def destroy_ui(self):
        self.root.destroy()