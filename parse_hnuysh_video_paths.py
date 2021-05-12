import requests
from bs4 import BeautifulSoup
import json
import time
"""
下载湖南大学杨老师的b站教学视频，离散数学很棒
步骤：
1. 爬取个人空间每页的视频地址+视频内容，按照上传时间添加编号
2. 从https://bilibili.iiilab.com/获得每个视频的资源地址

细节：
bilibili个人空间的视频列表是异步加载的，但异步的get请求有规律

"""

def construct_xhr_get_url(person_page:str, pg_number:int):
    user_id = person_page.split('/')[-2]
    xhr_get_url = "https://api.bilibili.com/x/space/arc/search?mid="+user_id +"&ps=30" +"&pn="+str(pg_number) +"&jsonp=jsonp"
    return xhr_get_url


def get_page_urls(person_page:str):
    '''
    对于其他人的个人主页同样适用；自动处理动态加载内容和多页问题
    :return: [{name, video_paths}]
    '''
    res_dict = {"total_this":0}

    r = requests.get(person_page)
    print("http status:", r.status_code, type(r.status_code))
    print("encoding:", r.encoding)

    # https://space.bilibili.com/349030303/video构造异步请求URL
    xhr_get_url = construct_xhr_get_url(person_page, pg_number=1)
    retry = 10
    xhr = requests.get(xhr_get_url)
    while xhr.status_code != 200 and retry > 0:
        xhr = requests.get(xhr_get_url)
        retry -= 1

    if xhr.status_code != 200:
        print("check net status")
        return res_dict
    # 解析总共条目
    j = json.loads(xhr.text)
    count_items = (int)(j.get("data").get("page").get("count"))# data.page.count
    print("total_items:", count_items)

    tol_page = count_items//30 + ((count_items%30)+29)//30
    print("total_page:", tol_page)
    cnt = 0
    for page_id in range(1, tol_page+1):

        xhr_get_url = construct_xhr_get_url(person_page, pg_number=page_id)
        print(xhr_get_url)
        retry = 10
        xhr = requests.get(xhr_get_url)
        while xhr.status_code != 200 and retry > 0:
            xhr = requests.get(xhr_get_url)
            retry -= 1

        if xhr.status_code != 200:
            print("check net status")
            return {"total_this": 0}

        # 解析当前页每个视频的名称和地址
        j = json.loads(xhr.text)
        video_dict = j.get("data").get("list").get("vlist")

        for video in range(len(video_dict)):

            cnt += 1
            res_dict.update({'0'*(3-len(str(cnt)))+str(cnt)+'_'+video_dict[video].get("title"):video_dict[video].get("bvid")})
            #print(res_dict)

    with open("./"+person_page.split('/')[-2]+"_videos.json" , "w") as dump_f:
        txt = str(res_dict)
        dump_f.write(txt)