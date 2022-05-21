# -*- encoding: utf-8 -*-
'''
@File    :   base_frame.py
@Time    :   2022/05/21 05:05:23
@Author  :   Martoriay 
@Version :   1.0
@Contact :   martoriay@protonmail.com
@License :   (C)Copyright 2021-2022
@Title   :   Base Frame for the notebook of main window
'''

import subprocess
import sys
import os

sys.path.append(os.path.abspath('./'))

import tkinter as tk 
from tkinter import *

class BaseFrame:
    manager_path="/Volumes/Movie"
    join=os.path.join
    def __init__(self,root=None):
        if root == None:
            self.root = tk.Tk()
        else:
            self.root = root
            
            
    def view_file(self,path):
        subprocess.call(['open',path])
            