# -*- encoding: utf-8 -*-
'''
@File    :   visualGUI.py
@Time    :   2022/06/07 02:19:02
@Author  :   Muyao ZHONG 
@Version :   1.0
@Contact :   zmy125616515@hotmail.com
@License :   (C)Copyright 2019-2020
@Title   :   
'''

import PySimpleGUI as sg

layout = [
    [sg.Text("测试链接："),sg.Input("http://wzdhm.cc/chapter/24801",key='test_url')],
    [sg.Button('添加规则',key='add_rule')]
]

window=sg.Window('Converter',layout)

while True:
    event,values= window.read()
    if event == sg.WIN_CLOSED:
        break 
    
    if event == 'add_rule':
        layout.append([sg.Text("选择器:"),sg.Input(key='selector')])
        window=sg.Window("爬虫",layout)
        print("Add a rule")
    
    