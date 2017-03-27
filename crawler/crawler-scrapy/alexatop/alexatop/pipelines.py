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
            solr.add([itmDict], fieldUpdates={'js_contents':'set'})
        else:
            '''commenting out blacklist verification for performance
            #check if blacklist
            try:
                domainList = {}
                if(itmDict['url']):
                    urlDom = "{0.netloc}".format(urlsplit(itmDict['url']))
                    if(urlDom):
                        domainList[urlDom]=1

                if(len(itmDict['urls']) > 0):
                    for url in itmDict['urls']:
                        urlDom = "{0.netloc}".format(urlsplit(url))
                        if(urlDom):
                            domainList[urlDom]=1

                if(len(itmDict['js_urls']) > 0):
                    for url in itmDict['js_urls']:
                        urlDom = "{0.netloc}".format(urlsplit(url))
                        if(urlDom):
                            domainList[urlDom]=1
                if(len(domainList) > 0):
                    solrBL = pysolr.Solr(SOLR_BLACKLIST_URL, timeout=10)
                    results = solrBL.search(q='url:(%s)'%' OR '.join(domainList.keys()),**{'rows':0}) #we only need hit count, not results
                    itmDict['blacklist_count'] = results.hits
                domainList.clear()
            except:
                raise
            finally:
                #print("Insert %s"%itmDict['alexa_rank'])
                solr.add([itmDict])'''
            solr.add([itmDict])
        return item
