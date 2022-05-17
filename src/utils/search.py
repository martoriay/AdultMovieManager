import requests
from bs4 import BeautifulSoup as bs

class Search:
    
    urls=[]
    hash_head="magnet:?xt=urn:btih:"
    
    def __init__(self,site_url="https://btsow.bar/search/"):
        self.url=site_url
        
    def get_url_list(self,keyword):
        
        url=self.url+keyword
        print("search start:"+url)
        html=requests.get(url)
        html.encoding = html.apparent_encoding
        content = html.text
        soup = bs(content,'html.parser')
        data_div = soup.find_all("div","data-list")
        return data_div
        
    def tiqu(self,data_div,lim=20):
        result=[]
        if len(data_div) == 0:
            print("没有找到内容")
        else:
            for n in data_div:
                text = n.find_all('a')
                for a in text:
                    # result.append(a['href'])
                    b=a.find_all('div',class_='col-xs-12 size-date visible-xs-block')
                    c=b[0].get_text()
                    
                    title=a['title']
                    
                    l_hash=str(a['href'])
                    tiqu_hash=l_hash[32:]
                    jiehe_hash=self.hash_head+tiqu_hash
                    movie=Movie(title,c,jiehe_hash)
                    result.append(movie)
                    if len(result)>=lim:
                        return result
        return result
        
    def search(self,key_word,lim=20):
        url=self.get_url_list(key_word)
        res=self.tiqu(url)
            
        if len(res)>=lim:
            res=res[:lim]
        return res
                    
                    
class Movie:
    
    title=""
    size=0
    date=""
    info=""
    hash=""
    def __init__(self,title,info,hash) :
        
        self.info=info
        self.hash=hash
        if len(title)>50:
            self.title=title[:50]
        else:
            l=len(title)
            self.title=title+" "*(50-l)
        
    def show(self):
        print("------------------------------------------")
        print(self.title,self.info,self.hash)
        
        
        
if __name__ == "__main__":
    s=Search()
    kw="fdafdsfsdafsa"
    res=s.search(kw)
    for i in res:
        i.show()
    
        
                    
        

        

        