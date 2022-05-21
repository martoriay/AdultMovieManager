from email import header
import os,requests
from urllib.request import urlopen,urlretrieve



class Downloader:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
    }
    def __init__(self,url,file_path):
        self.url=url
        self.file_path=file_path
        self.file_name=url.split('/')[-1]
        self.file_class=self.file_name.split('.')[-1]

    
    def download(self):
        
        file_name=os.path.join(self.file_path,self.file_name)
        if os.path.exists(file_name):
            print("%s is existing."%file_name)
        else:
            down_res=requests.get(self.url,headers=self.headers)
            try:
                with open(file_name,'wb') as f:
                    f.write(down_res.content)
                print("%s download completed."%file_name)
            except Exception as e:
                print("%s Download failed.Error: %s"%(file_name,e))

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
    }

def download(url,file_path):
    file_name=url.split('/')[-1]
    file_name=os.path.join(file_path,file_name)
    if os.path.exists(file_name):
        print("%s is existing."%file_name)
    else:
        down_res=requests.get(url,headers=headers)
        try:
            with open(file_name,'wb') as f:
                f.write(down_res.content)
            print("%s download completed."%file_name)
        except Exception as e:
            print("%s Download failed.Error: %s"%(file_name,e))      
            
def pic_down(urls,file_path):
    print("批量下载至%s"%file_path)
    s=requests.Session()
    for url in urls:
        file_name=url.split('/')[-1]
        file_name=os.path.join(file_path,file_name)
        if os.path.exists(file_name):
            print("%s is existing"%file_name)
        else:
            down_res=s.get(url, headers=headers)
            try:
                with open(file_name,'wb') as f:
                    f.write(down_res.content)
                # print("%s download completed."%file_name)
            except Exception as e:
                print("%s Download failed.Error: %s"%(file_name,e))  
    
        
        
if __name__ == "__main__":
    url="https://awscc3001.r18.com/litevideo/freepv/s/ssi/ssis00281/ssis00281_sm_w.mp4"
    file_path="./test_path"
    d=Downloader(url,file_path)
    d.download()
    
