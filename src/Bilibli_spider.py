import os
import random
import subprocess

import requests
import re  # 正则表达式
import json
import traceback

def gettitle(text):
    punctuation_pattern = re.compile(r'[^\w\s\u4e00-\u9fa5]')
    text = punctuation_pattern.sub('', text)[:10].replace(" ","_")
    return text

def getresponse(url,headers):
    # response = requests.get(url=url,headers=headers,proxies={'https': 'http://127.0.0.1:8889'})
    response = requests.get(url=url,headers=headers)
    return response


def download_fun(dirpath,title,url,headers):
    dir = os.path.split(dirpath)[0]
    if not os.path.exists(dir):
        os.makedirs(dir)
    response = getresponse(url=url, headers=headers)
    play_info = re.findall('<script>window.__playinfo__=(.*?)</script>', response.text)[0]
    # 把playinfo字符串转为dist类型
    json_data = json.loads(play_info)
    video_url = json_data['data']['dash']['video'][0]['baseUrl']
    audio_url = json_data['data']['dash']['audio'][0]['baseUrl']
    videopath = os.path.join(r"./" + title + ".mp4")
    audiopath = os.path.join(r"./" + title + ".mp3")
    video_content = getresponse(url=video_url, headers=headers).content  # 获取二进制数据
    with open(videopath, mode='wb') as f:
        f.write(video_content)
        print("---视频爬取成功！---")
    audio_content = getresponse(url=audio_url, headers=headers).content  # 获取二进制数据
    with open(audiopath, mode='wb') as f:
        f.write(audio_content)
        print("---音频爬取成功！---")
    print("合并音视频中.")
    ffmpegpath = os.path.abspath("./ffmpeg-5.1.1/bin/ffmpeg")
    cmd = f'{ffmpegpath} -i {videopath} -i {audiopath} -c:v copy -c:a aac -strict experimental {dirpath}'
    p = subprocess.Popen(cmd, shell=True)
    return_code = p.wait()  # 等待子进程结束，并返回状态码；
    os.remove(audiopath)
    os.remove(videopath)
    print("-----------爬取成功！---------")


def allpage(url,num=0):
    index = 0
    headers_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
        ,
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0'
    ]
    headers = {
        "referer": "https://search.bilibili.com/",
        'user-agent': ""}
    headers['user-agent'] = random.choice(headers_list)
    response = getresponse(url=url, headers=headers)
    initial_state = re.findall('<script>window.__INITIAL_STATE__=(.*?)</script>', response.text)[0]
    # 把playinfo字符串转为dist类型
    json_data = json.loads(initial_state.split(";(")[0])
    onetitle = json_data['videoData']['title']
    title = gettitle(onetitle)
    video_url_list = json_data['videoData']['pages']
    print(f"-----------链接下有{len(video_url_list)}个视频选集，开始下载！-----------")
    if num == 0:
        for video in video_url_list:
            index += 1
            viedotitle = video["part"]
            title1 = str(index)+gettitle(viedotitle)
            if title1 == "":
                title1 = title
            videopage = video["page"]
            newurl = url+f"?p={videopage}"
            dirpath = os.path.join(f"./Data/{title}/" + title1 + ".mp4")
            print(f"******{viedotitle}正在下载！******")
            download_fun(dirpath,title1,newurl,headers)
    elif num > 0:
        video = video_url_list[num-1]
        viedotitle = video["part"]
        title1 = str(index) + gettitle(viedotitle)
        if title1 == "":
            title1 = title
        videopage = video["page"]
        newurl = url + f"?p={videopage}"
        dirpath = os.path.join(f"./Data/{title}/" + title1 + ".mp4")
        print(f"******{viedotitle}正在下载！******")
        download_fun(dirpath, title1, newurl, headers)


def action():
    input_url = input("请输入下载视频的链接：")
    url = input_url.split("?")[0]
    allpage(url,num=5)
    action()
action()
