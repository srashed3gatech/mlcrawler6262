# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pysolr
from urllib.parse import urlsplit

SOLR_CORE_URL = 'http://localhost:8983/solr/crawler/'
SOLR_BLACKLIST_URL = 'http://localhost:8983/solr/blacklist/'

class TutorialPipeline(object):
    def process_item(self, item, spider):
        solr = pysolr.Solr(SOLR_CORE_URL, timeout=10)
        itmDict = dict(item)
        itmDict['id'] = itmDict['pk']
        print(itmDict.keys())
        if(len(itmDict.keys()) == 3): #update only
            print('UPDATE SORL')
            #print(itmDict)
            #itemToUpdate = {'id':itmDict['pk'],'js_urls':{'add':itmDict['js_urls'].keys()}}
            solr.add([itmDict], fieldUpdates={'js_contents':'set'})
            #print([itemToUpdate])
        else:
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
                #print(domainList)
                print(' OR '.join(domainList.keys()))
                if(len(domainList) > 0):
                    solrBL = pysolr.Solr(SOLR_BLACKLIST_URL, timeout=10)
                    results = solrBL.search(q='url:(%s)'%' OR '.join(domainList.keys()),**{'rows':0}) #we only need hit count, not results
                    itmDict['blacklist_count'] = results.hits
                domainList.clear()
                print("blacklist count# : %s"%itmDict['blacklist_count'])
            except:
                raise
            finally:
                print('INSERT INTO SORL')
                #print(itmDict['url'])
                solr.add([itmDict])

            #print(itmDict)



        #solr = pysolr.Solr(SOLR_CORE_URL, timeout=10)
        #d = dict(item)
        #d['id'] = d['pk'] # Solr requires an id parameter
        #solr.add([d])
        return item
