import scrapy
from pyquery import PyQuery

class WeiboSpider(scrapy.Spider):
    name = "weibo"
    allowed_domains = ["s.weibo.com"]
    start_urls = ["https://s.weibo.com/top/summary/"]

    def parse(self, response):
        doc = PyQuery(response.text)
        rows = doc("#pl_top_realtimehot > table > tbody > tr")
        rank_list = []
        for row in rows:
            row = PyQuery(row)
            title = row.find('a').text()
            rank = row.find('.ranktop').text()
            hot = row.find('span').text()
            link = row.find('a').attr('href')
            tag = row.find('.icon-txt').text()
            rank_item = {
                'title': title, 
                'rank': rank, 
                'hot': hot, 
                'tag': tag,
                'link': link
            }
            if hot:
                rank_list.append(rank_item)
        yield rank_list
