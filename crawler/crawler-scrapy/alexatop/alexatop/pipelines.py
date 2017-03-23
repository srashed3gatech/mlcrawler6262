# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pysolr

SOLR_CORE_URL = 'http://localhost:8983/solr/crawler/'

# Date formatting
SOLR_DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

def format_date(dt, fmt=SOLR_DATE_FORMAT):
    return datetime.strftime(dt, fmt)

TODAY = format_date(datetime.now())

class AlexaPipeline(object):
    def process_item(self, item, spider):
        # Check blacklist if URL
        return item

class SolrPipeline(object):
    solr = pysolr.Solr(SOLR_CORE_URL, timeout=10)

    def process_item(self, item, spider):
        # Append timestamp to item
        item['timestamp'] = TODAY

        self.solr.add([itmDict])

        return item
