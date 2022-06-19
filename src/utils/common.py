import re,os,sys
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

def get_soup(url,debug=False,encode="",headers="",proxy=False):
    if headers=="":
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15',
            }
    proxies={
        'http':'http://127.0.0.1:7890',
        'https':'http://127.0.0.1:7890'
    }
    if proxy:
        html=requests.get(url,headers=headers,proxies=proxies)
    else:
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
    
    
def download_single(url,path,name="",headers="",proxy=True,debug=False):
    if headers=="":
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15',
            }
    proxies={
        'http':'http://127.0.0.1:7890',
        'https':'http://127.0.0.1:7890'
    }
    if name == "":
        file_name = url.split('/')[-1]
    else:
        file_name = name
    file_name = os.path.join(path,file_name)
    if os.path.exists(file_name):
        if debug:
            print("%s is exists."%file_name)
    else:
        if proxy:
            down_res=requests.get(url,headers=headers,proxies=proxies)
        else:
            down_res=requests.get(url,headers=headers)
            
        c=down_res.status_code
        if c>=400:
            print("Didnt get the content with code %d"%c,url,file_name)
            return 
        
        try:
            with open(file_name,'wb') as f:
                f.write(down_res.content)
            if debug:
                print("%s downloaded."%file_name)
        except Exception as e:
            print("Download Single FIle %s Error:"%file_name,e)
            
def divide_len_by_worker(length,worker):
    pointers=[round(i/worker*length) for i in range(worker)]
    res=[]
    for i in range(worker):
        if i==worker-1:
            res.append([pointers[-1],length])
            break
        else:
            start=pointers[i]
            end=pointers[i+1]
            res.append([start,end])
    return res

def parser_url(url):
    urls=url.split('/')
    name=urls.pop(-1)
    res=''
    for u in urls:
        res+=u+'/'
    return res,name
        

    


if __name__ == '__main__':
    print(deparser_id("ipx00080"))