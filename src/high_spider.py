import os
import random
import time
import csv
import requests
import re  # 正则表达式
import pprint
import json
import subprocess


def getresponse(url,headers,data=""):
    response = requests.get(url=url,headers=headers,params=data)
    return response

def replace_func(m):
    new_num = 30000 + m
    return str(new_num) + '.m4s'
def gettitle(text):
    punctuation_pattern = re.compile(r'[^\w\s\u4e00-\u9fa5]')
    text = punctuation_pattern.sub('', text).replace(" ","_")
    return text

def allpage(pageNum,keyword,fnval=0,videotime=0):
    tasklist = r"./hat_tasklist.cvs"
    bvidList = []
    if os.path.exists(tasklist):
        file = open(tasklist)
        bvid = list(csv.reader(file))  # 读取出来的列表
        for Lbvid in bvid:
            bvidList.append(Lbvid[0])
    picpath = '../Data/' +keyword
    if not os.path.exists(picpath): os.makedirs(picpath)

    num = 0
    url = "https://api.bilibili.com/x/web-interface/wbi/search/type"
    data = {
        '__refresh__': 'true',
        '_extra': '',
        'context': '',
        'page': '',
        'page_size': '36',
        'from_source': '',
        'from_spmid': '333.1007',
        'platform': 'pc',
        'highlight': '1',
        'single_column': '0',
        'keyword': keyword,
        'category_id': '',
        'search_type': 'video',
    }
    user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 "
        "Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
    ]

    headers = {
        "referer": "https://search.bilibili.com/",
        'cookie':"",#自行登录b站后获取cookie
        'user-agent': ""
    }
    headers['user-agent'] = random.choice(user_agent_list)
    for page in range(pageNum):
        page = page+1
        print("#"*20+f"爬取第{page}页"+"#"*20)
        data['page'] = str(page)
        response = getresponse(url=url,headers=headers,data=data)
        if response.status_code != 200:
            print("页面获取失败")
            continue
        result = response.json()['data']['result']
        for index in result:
            headers['user-agent'] = random.choice(user_agent_list)
            try:
                bv_id = index['bvid']
                if bv_id in bvidList:
                    print("!"*20+f"{bv_id}已经爬取过了"+"!"*20)
                    continue
                title = index['title'].replace('<em class="keyword">','').replace('</em>','')
                title = gettitle(title)
                print("正在爬取"+bv_id, title)
                try:
                    #获取cid等信息
                    oneurl = f"https://api.bilibili.com/x/player/pagelist?bvid={bv_id}"
                    res_id = requests.get(oneurl, headers=headers).json()
                    duration = int(res_id['data'][0]['duration'])

                    #获取视频的时长，如果有传入限制参数即判断是否超过限制，超过则不爬取，不传入则默认不限制
                    if videotime != 0 and duration > videotime:
                        print("~~~~~~~~~~视频时长超限制，不爬取！~~~~~~~~~~")
                        continue
                    if res_id['code'] != 0:
                        print("~~~~~~~~~~cid获取失败！~~~~~~~~~~")
                        continue
                    cid = res_id['data'][0]['cid']

                    #获取视频所有清晰度的视频链接
                    highaccept_url = f"https://api.bilibili.com/x/player/playurl?cid={cid}&bvid={bv_id}&fnval=80"
                    video_json = getresponse(url=highaccept_url,headers=headers)
                    if video_json.json()['code'] != 0:
                        print("~~~~~~~~~~各清晰度的视频url获取失败！~~~~~~~~~~")
                        continue
                    video_list = video_json.json()['data']['dash']['video']
                    #判断是否有设置清晰度，如果没有就默认最高清晰度
                    if fnval == 0:
                        index = 0
                    else:#如果视频没有指定清晰度，就默认最高清晰度
                        for x in video_list:
                            if x['id'] == fnval:
                                index = video_list.index(x)
                                break
                            else:
                                index = 0
                    video_url = video_list[index]['baseUrl']
                    video_content = getresponse(url=video_url,headers=headers)
                    #如果视频链接爬取失败，就爬取备用链接，如果备用链接都爬取失败就跳过
                    if video_content.status_code != 200:
                        for i in video_list[index]['backupUrl']:
                            video_content = getresponse(url=i,headers=headers)
                            if video_content.status_code == 200:
                                break
                        if video_content.status_code != 200:#备用链接都爬取失败，即跳过
                            print("~~~~~~~~~~爬取失败！~~~~~~~~~~")
                            continue
                    num += 1
                    videopath = os.path.join(picpath,str(num)+title+".mp4")
                    with open(videopath,mode='wb') as f:
                        f.write(video_content.content)
                    bvidList.append(bv_id)
                    with open(tasklist, 'a+', newline="") as f:
                        csv_flie = csv.writer(f, dialect='excel')
                        csv_flie.writerow([bv_id])
                    print("-----------爬取成功！---------")
                except:
                    print("~~~~~~~~~~爬取失败！~~~~~~~~~~")
            except:
                continue
            time.sleep(3)
pageNum = 5#每页36个视频
#16: 360p
# 32: 480p
# 64: 720p
# 80: 1080p 非会员最大可获取的清晰度
# 112: 1080p+
# 116: 4K
fnval = 80
videotime = 600
# keywords = ["戴渔夫帽","戴贝雷帽","戴遮阳帽","跑步戴帽子","戴毛线帽","戴针织帽","戴军训帽","戴帽子发型","修饰脸型的帽子"]
keywords = []
for keyword in keywords:
    allpage(pageNum,keyword,fnval,videotime)#不传入fnval参数的时候默认获取最高的清晰度，如果想获取其他清晰度，可以传入fnval参数，参数值为上面的数字，video_time参数为限制爬取视频时长，单位为秒
