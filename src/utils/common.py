import re
import requests
from bs4 import BeautifulSoup as bs

def id_parser(id):
    if id.startswith('dfe'):
        id='2'+id
    elif id.startswith('jukf'):
        id='h_227'+id
    elif id.startswith('milk'):
        id='h_1240'+id
    elif id.startswith('ddff'):
        id='111'+id
    elif id.startswith('fsdss'):
        id='1'+id
    elif id.startswith('dv'):
        id='53'+id
    elif id.startswith('sdde'):
        id='1'+id
    elif id.startswith('ienfh'):
        id='2'+id
    elif id.startswith('hodv'):
        id='5642hodv'+id[-5:]
    elif id.startswith('pih'):
        id='1'+id
    elif id.startswith('akdl'):
        id='1'+id
    return id

def deparser_id(id):
    if id.startswith('2') or id.startswith('1'):
        id=id[1:]
    elif id.startswith('53'):
        id=id[2:]
    elif id.startswith("111"):
        id=id[3:]
    elif id.startswith("h_227"):
        id=id[5:]
    elif id.startswith("h_1248"):
        id=id[6:]
    elif id.startswith("5642hodv"):
        id="HODV-"+id[8:]
        return id
    
    start=id.find('00')
    title=id[:start].upper()
    num=id[start+2:]
    return title+'-'+num

def get_soup(url,debug=False,encode=""):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15',
        }
    html=requests.get(url,headers=headers)
    if debug:
        print("Response:",html.status_code)
    if encode=="":
        html.encoding = html.apparent_encoding
    else:
        html.encoding = encode
    soup = bs(html.text,features="html.parser")
    return soup

def ui_clean(ui):
    for w in ui.winfo_children():
        w.pack_forget()
        
def get_attrs_from_soup(soup,selector,attrs):
    elements=soup.select(selector)
    res=[]
    for e in elements:
        dct={}
        for attr in attrs:
            if attr=='text':
                t=e.get_text()
            else:
                t=e.get(attr)
            dct[attr]=t 
        res.append(dct)
    return res
        
def get_attr_from_soup(soup,selector,attr):
    elements=soup.select(selector)
    res=[]
    for e in elements:
        if attr=='text':
            t=e.get_text()
        else:
            t=e.get(attr)
        res.append(t)
    return res

def get_info_by_rule(soup,rule):
    elements=soup.select(rule["selector"])
    

    


if __name__ == '__main__':
    print(deparser_id("ipx00080"))