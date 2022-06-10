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
sys.path.append(os.path.abspath('./'))
from utils.common import get_soup 



class Ruler:
    @abstractmethod
    def make_rule(name,selectors,attr,check_attr,check_value,attrs):
        rule={
            'name':name,
            'selector':selectors,
            'attr':attr,
            'check_attr':check_attr,
            'check_value':check_value,
            'attrs':attrs
        }
        return rule
    
    @abstractmethod
    def make_attr_selctor(name,selector,attr,check_attr,check_value):
        res={
            'name':name,
            'selector':selector,
            'attr':attr,
            'check_attr':check_attr,
            'check_value':check_value
        }
        return res
    
