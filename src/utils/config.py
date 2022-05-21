# -*- encoding: utf-8 -*-
'''
@File    :   config.py
@Time    :   2022/05/12 14:49:59
@Author  :   Muyao ZHONG 
@Version :   1.0
@Contact :   zmy125616515@hotmail.com
@License :   (C)Copyright 2019-2020
@Title   :   About the configuration.
'''

import json

def get_config(path,name=None):
    with open(path,'r') as f:
        config=json.load(f)
    if name is None:
        return config
    else:
        try:
            tmp=config[name]
            return tmp
        except:
            print("No name is found in config file.")
            return None
        
def set_config(path,dct):
    with open(path,'r') as f:
        config=json.load(f)
        config.update(dct)
    with open(path,'w') as f:
        json.dump(config,f)
        

        
        