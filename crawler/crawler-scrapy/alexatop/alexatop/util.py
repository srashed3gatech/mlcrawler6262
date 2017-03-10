import os
import csv
import json
import hashlib
import requests
from zipfile import ZipFile
from collections import OrderedDict

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

    # Clean up (delete .zip file)
    os.remove('top1m.zip')

    return data

def compute_md5(s):
    return hashlib.md5(s.encode('utf-8')).hexdigest()

def dict_to_json(d):
    '''Convert a dict to JSON.'''
    # Convert a binary dict to clean dict for JSON encoding
    # http://stackoverflow.com/questions/33137741/fastest-way-to-convert-a-dicts-keys-values-from-bytes-to-str-in-python3
    def convert(data):
        if isinstance(data, list):   return data[0].decode()
        if isinstance(data, bytes):  return data.decode()
        if isinstance(data, dict):   return dict(map(convert, data.items()))
        if isinstance(data, tuple):  return map(convert, data)
        return data

    return json.dumps(convert(d))
