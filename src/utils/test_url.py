import requests
from bs4 import BeautifulSoup as bs


headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15',
        "Accept-Language": "zh-CN,zh-Hans;q=0.9"
    }   
url="https://www.r18.com/videos/rankings/movies/?type=daily&dmmref=pc_header"
url = "https://www.r18.com/videos/vod/movies/actress/?dmmref=pc_header"
html=requests.get(url,headers=headers)
html.encoding=html.apparent_encoding
soup = bs(html.text,features="html.parser")
cm = soup.select(".main")
print(cm)