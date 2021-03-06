# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BLItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    full_html = scrapy.Field()
    url = scrapy.Field()
    date = scrapy.Field()
    timestamp = scrapy.Field()
    pk = scrapy.Field()
    full_hash = scrapy.Field()
    body_hash = scrapy.Field()
    head_hash = scrapy.Field()
    urls = scrapy.Field()
    urls_hash = scrapy.Field()
    js_urls = scrapy.Field()
    headers = scrapy.Field()
    latency = scrapy.Field()
    crawl_status = scrapy.Field()
    label = scrapy.Field()
