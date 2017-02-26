from ..items import AlexaItem

import scrapy
import requests

import csv
import random
from zipfile import ZipFile
from collections import OrderedDict

# 1. Grab Alex top 1M list from source
# 2. Extract archive
# 3. Parse the csv and extract the URLs
# 4. Start crawling

ALEXA_LIST_URL = 'http://s3.amazonaws.com/alexa-static/top-1m.csv.zip'

ALEXA_TOP_100 = OrderedDict(
    [('1', 'http://google.com'), ('2', 'http://youtube.com'), ('3', 'http://facebook.com'), ('4', 'http://baidu.com'), ('5', 'http://yahoo.com'), ('6', 'http://wikipedia.org'), ('7', 'http://google.co.in'), ('8', 'http://qq.com'), ('9', 'http://tmall.com'), ('10', 'http://sohu.com'), ('11', 'http://google.co.jp'), ('12', 'http://taobao.com'), ('13', 'http://amazon.com'), ('14', 'http://live.com'), ('15', 'http://vk.com'), ('16', 'http://twitter.com'), ('17', 'http://instagram.com'), ('18', 'http://360.cn'), ('19', 'http://sina.com.cn'), ('20', 'http://linkedin.com'), ('21', 'http://jd.com'), ('22', 'http://google.de'), ('23', 'http://google.co.uk'), ('24', 'http://reddit.com'), ('25', 'http://google.fr'), ('26', 'http://yahoo.co.jp'), ('27', 'http://google.ru'), ('28', 'http://weibo.com'), ('29', 'http://hao123.com'), ('30', 'http://google.com.br'), ('31', 'http://ebay.com'), ('32', 'http://yandex.ru'), ('33', 'http://google.it'), ('34', 'http://msn.com'), ('35', 'http://google.es'), ('36', 'http://google.com.hk'), ('37', 'http://bing.com'), ('38', 'http://wordpress.com'), ('39', 'http://onclkds.com'), ('40', 'http://t.co'), ('41', 'http://detail.tmall.com'), ('42', 'http://netflix.com'), ('43', 'http://ok.ru'), ('44', 'http://aliexpress.com'), ('45', 'http://microsoft.com'), ('46', 'http://google.ca'), ('47', 'http://tumblr.com'), ('48', 'http://google.com.mx'), ('49', 'http://blogspot.com'), ('50', 'http://stackoverflow.com')]
)

def grab_alexa(count=0):
    '''Grabs Alexa top 1M list and returns it as a OrderedDict int (rank) -> str (url)'''
    if ALEXA_TOP_100 != None:
        return ALEXA_TOP_100

    # Grab ZIP and store on disk
    resp = requests.get(ALEXA_LIST_URL)
    archive = resp.content

    with open('top1m.zip', 'wb') as f:
        f.write(archive)

    data = OrderedDict()
    
    # Unzip, read, and parse CSV
    with ZipFile('top1m.zip', 'r') as zf:
        lines = [line.decode() for line in zf.open('top-1m.csv', 'r').readlines()]

        if count > 0:
            lines = lines[:count]
        else:
            raise Exception('Please pass in a positive count.')
        
        # Parse CSV and convert to dict format
        for row in csv.reader(lines):
            data[row[0]] = 'http://' + row[1]

    return data

class AlexaSpider(scrapy.Spider):
    name = "alexa"
    
    def start_requests(self):
        urls = [v for v in list(grab_alexa(10).values())]

        for url in urls:
            self.user_agent = random.choice(self.settings['USER_AGENTS'])
            yield scrapy.Request(url=url, callback=self.parse)
    
    def parse(self, response):
        body = response.text
        title = response.xpath('//head/title/text()').extract() # XPath syntax
        
        return AlexaItem(url=response.url, title=title)
        