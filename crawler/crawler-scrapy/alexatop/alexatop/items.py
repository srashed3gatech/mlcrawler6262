# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class AlexaItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    rank = scrapy.Field()
    timestamp = scrapy.Field()
    pk = scrapy.Field()
    full_hash = scrapy.Field()
    body_hash = scrapy.Field()
    head_hash = scrapy.Field()
    urls = scrapy.Field()
    urls_hash = scrapy.Field()
    js_urls = scrapy.Field()
    js_content = scrapy.Field()
    headers = scrapy.Field()
    latency = scrapy.Field()
