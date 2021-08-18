import os
from os import path
from sys import argv
from time import sleep

import requests
from requests.api import get

from faker import Factory
from pyquery import PyQuery as pq
from requests.sessions import Session

ignore_error = True # 忽略错误， 为 False 即报错后立即退出
enable_proxy = True # 是否使用代理，代理池及配置见 https://github.com/jhao104/proxy_pool
base_url = "https://m.onlionli.cn/"  # 网站网址
out_dir = "output/"  # 输出路径
sleep_per_pic = 0.2  # 每下载一张图片休眠时间，降低服务器压力
sleep_per_chapter = 1.5  # 每下载一个章节休眠时间，降低服务器压力
time_out = 35 # 超时时间

faker = Factory.create()
def get_headers():
    headers = {}
    headers["User-Agent"] = faker.user_agent()
    return headers

def get_proxy():
    if enable_proxy == False:
        return {}
    res = requests.get('http://localhost:5010/get')
    if res.text is None:
        sleep(0.2)
        res = requests.get('http://localhost:5010/get')
    proxy = res.json()
    p_protocol = 'http'
    if proxy['https']:
        p_protocol = 'https'
    return {
        p_protocol: proxy['proxy']
    }

class ComicDownloader:
    def __init__(self, comic_id):
        self.id = comic_id
        self.indexes = []
        self.name = ""
        self.download_dir = ""
        self.download_pics = []
        self.downloaded_txt = ""

    """ 加载下载记录 """
    def load_status(self):
        self.downloaded_txt = "{}/downloaded.txt".format(self.download_dir)
        if self.download_dir and path.isfile(self.downloaded_txt):
            with open(self.downloaded_txt) as f:
                self.download_pics = f.readlines()

    """ 检查是否已下载该图片 """

    def check_is_downloaded(self, url):
        if len(self.download_pics) == 0:
            return False
        for line in self.download_pics:
            line = line.replace('\r','').replace('\n', '')
            if line == url:
                print('该图片已下载：', url)
                return True
        return False

    """ 开始爬取 """
    def start(self):
        self.get_index()
        for index, chapter in enumerate(self.indexes):
            url = "{}{}".format(base_url, chapter.get("href"))
            title = chapter.get("title")
            try:
                self.download_chapter(title, index + 1, url)
            except Exception as e:
                print(e)
                if ignore_error == False:
                    raise

    """ 获取目录 """
    def get_index(self):
        url = "{}book/{}".format(base_url, self.id)
        req = requests.get(url, headers=get_headers(), proxies=get_proxy(), timeout=time_out)
        doc = pq(req.text)
        self.name = doc("title").text()
        self.indexes = doc("a[class='chapteritem']")
        print("{} 共找到 {} 个章节".format(self.name, len(self.indexes)))

        if len(self.indexes) < 1:
            return

        # 创建目录
        self.download_dir = "{}/{}".format(out_dir, self.name)
        if (
            path.exists(self.download_dir) == False
            or path.isdir(self.download_dir) == False
        ):
            os.makedirs(self.download_dir)
        self.load_status()

    """ 下载章节 """

    def download_chapter(self, title, chapter_index, url):
        if len(url) < 1:
            return
        
        """ 相同章节复用连接 """
        session = requests.session()
        session.headers = get_headers()
        session.headers["referer"] = url
        session.proxies = get_proxy()

        req = session.get(url, timeout=time_out)
        doc = pq(req.text)
        pics = doc("img[class='lazy']")
        chapter_dir = "{}/{}".format(self.download_dir, chapter_index)
        if pics and path.isdir(chapter_dir) == False:
            os.makedirs(chapter_dir)
            filename = "{}/title.txt".format(chapter_dir)
            with open(filename, mode="w") as f:
                f.write(title)
                f.close()
        for index, item in enumerate(pics):
            url = item.get("data-original")
            try:
                self.download_img(session, url, chapter_index, index)
            except Exception as e:
                print(e)
                if ignore_error == False:
                    raise

        if sleep_per_chapter > 0:
            sleep(sleep_per_chapter)

    """ 下载图片 """

    def download_img(self, session:Session, url:str, chapter_index:int, pic_index:int):
        filepath = "{}/{}/{}.jpg".format(self.download_dir, chapter_index, pic_index)
        if self.check_is_downloaded(url):
            return
        req = session.get(url, timeout=time_out)
        with open(filepath, mode="wb") as f:
            f.write(req.content)
            print("【{}】保存成功！".format(filepath))
            f.close()
            """ 写入记录 """
            with open(self.downloaded_txt, mode="a") as log:
                log.write("{}\r\n".format(url))
                log.close()
        sleep(sleep_per_pic)


if __name__ == "__main__":
    comic_id = ""
    if len(argv) < 2:
        comic_id = input("请输入要爬取的漫画 id (数字)：")
        if len(comic_id) < 3:
            print("漫画 id 应为 3 个以上数字！")
            exit(0)
    else:
        comic_id = argv[1]
    woker = ComicDownloader(comic_id=comic_id)
    woker.start()
