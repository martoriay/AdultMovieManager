# -*- encoding: utf-8 -*-
'''
@File    :   engin_frame.py
@Time    :   2022/05/21 05:04:00
@Author  :   Martoriay 
@Version :   1.0
@Contact :   martoriay@protonmail.com
@License :   (C)Copyright 2021-2022
@Title   :   Engin Frame UI
'''

import sys
import os
sys.path.append(os.path.abspath('./'))

from ui.base_frame import BaseFrame
from engin.javday import Javday


class EnginFrame(BaseFrame):
    def __init__(self,root=None):
        super().__init__(root)
        
