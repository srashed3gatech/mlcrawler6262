# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pysolr

SOLR_CORE_URL = 'http://localhost:8983/solr/crawler/'

class AlexaPipeline(object):
    def process_item(self, item, spider):
        # Check blacklist if URL
        return item

class SolrPipeline(object):
    def process_item(self, item, spider):
        solr = pysolr.Solr(SOLR_CORE_URL, timeout=10)
        itmDict = dict(item)
        itmDict['id'] = itmDict['pk']
        if(len(itmDict.keys()) == 3): #update only
            solr.add([itmDict], fieldUpdates={'js_urls':'add'})
        else:
            solr.add([itmDict])
        return item
