"""
@Descripttion: 
@version: 
@Date: 2020-07-20 12:39:37
LastEditTime: 2020-11-28 15:30:45
"""
# -*- coding: utf-8 -*-
import os, requests, chardet, re, sqlite3, threading
from lxml import etree
from requests.exceptions import RequestException
from requests.adapters import HTTPAdapter
from powerspider.Download import downloader
from powerspider.toolSet.Ua import ua

# site_url = '%s//%s' % (response.url.split('/')[0], response.url.split('/')[2]) 获取域名

# project_dir = os.path.abspath(os.path.dirname(__file__))
# IMAGES_STORE = os.path.join(project_dir, 'xgmn')
# file_path = 'u://uploadfile' if os.name == 'nt' else '/Volumes/RamDisk/uploadfile'


def get_res(url, referer=None):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:68.0) Gecko/20100101 Firefox/68.0",
        # "referer": "%s" %(referer)
    }
    s = requests.session()
    s.mount("http://", HTTPAdapter(max_retries=3))
    s.mount("https://", HTTPAdapter(max_retries=3))
    try:
        response = s.get(url, headers=headers)
        if response.status_code == 200:
            if "html" in response.headers["Content-Type"]:
                encode = chardet.detect(response.content)
                print("页面编码为：", encode["encoding"])
                # response.encoding = 'utf-8' # 直接转为utf8
                response.encoding = encode["encoding"]
            return response
        return None
    except Exception as e:
        print(e)


def get_last():
    conn_sql3 = sqlite3.connect(sqlite_db)
    sql3_cur = conn_sql3.cursor()
    sql = "SELECT id, director_url FROM av_list WHERE director_url <> ''"  # 获取最后一条数据
    sql3_cur.execute(sql)
    res_db = sql3_cur.fetchall()
    return res_db


def parse(url, img_list=None):
    site_url = "%s//%s" % (url.split("/")[0], url.split("/")[2])
    referer = os.path.dirname(url)
    cdn = "https://p1.plmn5.com"
    res = downloader(url, method=True)
    res_ele = etree.HTML(res.text)
    title = res_ele.xpath('//h1[@class="article-title"]/text()')[0]
    imgs = [cdn + i for i in res_ele.xpath("//p/img/@src")]
    img_list.append(img)
    if ("下一页" in res_ele.xpath('//div[@class="pagination"]/ul[1]/a/text()')[-1]):  # 判断还有下一页
        next_url = "%s%s" % (site_url, res_ele.xpath('//div[@class="pagination"]/ul[1]/a/@href')[-1],)
        # print(next_url)
        parse(next_url, img_list)
    return title, img_list


def pares_page(url):
    base_path = r"u:\uploadfile"
    av_id = "Vol." + re.findall("\d+", title)[0].capitalize()
    for i, img in enumerate(img_list):
        print("[%s/%s]" % (i, len(img_list)), end="\r")
        # print('[%s/%s]' % (i, len(img_list)), end='')
        cname = url.split('/')[3]
        file_path = "%s/%s/%s" % (base_path, cname, av_id)
        full_path = "%s/%s.jpg" % (file_path, i + 1)
        down_file(img, file_path, full_path, url)


def main():
    global sqlite_db, img_list
    sqlite_db = r"U:\2nvshen.db"
    img_list = []
    res_db = get_last()
    for db in res_db:
        url = db[1]
        id = db[0]
        print(url)
        title, img_list = parse(url, img_list=[])
        print("共%s张" % (len(img_list)))
        # print(title, img_list)
        pares_page(title, img_list, url)
        up_sql(id, len(img_list))


def down_file(url, file_path, full_path):
    if not os.path.exists(file_path):
        print("创建文件夹")
        os.makedirs(file_path)
    if not os.path.exists(full_path):
        res = downloader(url)
        with open(full_path, "wb") as f:
            f.write(res.content)
    # # 使用多线程下载
    #     t = threading.Thread(target=down_file,args=(img, file_path, full_path))
    #     t.start()
    # while threading.activeCount() !=1:
    #     pass


def save_sql(item):
    conn_sql3 = sqlite3.connect(sqlite_db)
    sql3_cur = conn_sql3.cursor()
    sql = (
        'insert into av_list(id,linkid,title,av_id,release_date,len,director,studio,label,series,genre,stars,director_url,studio_url,label_url,series_url,stars_url,bigimage,image_len) values(\
        "%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")'
        % (
            item["id"],
            item["linkid"],
            item["title"],
            item["av_id"],
            item["release_date"],
            item["len"],
            item["director"],
            item["studio"],
            item["label"],
            item["series"],
            item["genre"],
            item["stars"],
            item["director_url"],
            item["studio_url"],
            item["label_url"],
            item["series_url"],
            item["stars_url"],
            item["bigimage"],
            item["image_len"],
        )
    )
    try:
        sql3_cur.execute(sql)
        conn_sql3.commit()
        print("添加成功:%s" % (item["av_id"]))
    except Exception as e:
        print("数据库写入错误")
        print(e)
        conn_sql3.rollback()
        stop_get = input("按任意键继续")


if __name__ == "__main__":
    main()
