'''
Descripttion: 192tp图片站，经常不能访问，使用 gke.mybinder.org 代理下载
version: 
Date: 2021-10-16 12:46:49
LastEditTime: 2021-10-16 12:48:04
'''
# -*- coding: utf-8 -*-
import os, requests, chardet, re
from lxml import etree
from requests.exceptions import RequestException
from requests.adapters import HTTPAdapter

# site_url = '%s//%s' % (response.url.split('/')[0], response.url.split('/')[2]) 获取域名
# site_url = url.rsplit("/", 2)[0]

# project_dir = os.path.abspath(os.path.dirname(__file__))
# IMAGES_STORE = os.path.join(project_dir, 'xgmn')
# file_path = 'u://uploadfile' if os.name == 'nt' else '/Volumes/RamDisk/uploadfile'

def get_res(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:68.0) Gecko/20100101 Firefox/68.0"
    }
    s = requests.session()
    s.mount("http://", HTTPAdapter(max_retries=3))
    s.mount("https://", HTTPAdapter(max_retries=3))
    try:
        response = s.get(url, headers=headers)
        if response.status_code == 200:
            if "html" in response.headers["Content-Type"]:
                encode = chardet.detect(response.content)
                # print("页面编码为：", encode["encoding"])
                # response.encoding = 'utf-8' # 直接转为utf8
                response.encoding = encode["encoding"]
            return response
        return None
    except Exception as e:
        print(e)

        
def parse(url):
    res = get_res(url)
    res_ele = etree.HTML(res.text)
    img = res_ele.xpath('//center/img/@lazysrc')[0]

    return img


def pares_page(url, imgs=None):
    print(url)
    res = get_res(url)
    res_ele = etree.HTML(res.text)
    imgs.append(parse(url))
    try:
        next_url = res_ele.xpath('//a[@class="nextpagebtn"]/@href')[0]
        print('next_url:', next_url)
        if '_' not in next_url:
            return imgs
        pares_page(next_url, imgs)
    except:
        next_url = None
        print('完成解析')
    
    return imgs


def main():
#     num = '2122'
    # 需下载数字前后各+1
    for num in range(2125, 2132):
        url = 'https://www.192tp.com/gc/bl/beautyleg%s.html' % str(num)
        imgs = []
        img_list = pares_page(url, imgs)
        print('共%s张图片' % (len(img_list)))
        for v, i in enumerate(img_list):
            file_path = './beautyleg/No.%s' % str(num)
            full_path = '%s/%s.jpg' % (file_path, v+1)
            down_file(i, file_path, full_path)


def down_file(url, file_path, full_path):
    if not os.path.exists(file_path):
        print("创建文件夹")
        os.makedirs(file_path)
    if not os.path.exists(full_path):
        res = get_res(url)
        with open(full_path, "wb") as f:
            f.write(res.content)


if __name__ == "__main__":
    main()
