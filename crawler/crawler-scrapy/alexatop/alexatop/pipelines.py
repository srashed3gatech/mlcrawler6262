# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pysolr

SOLR_BLACKLIST_URL = 'http://localhost:8983/solr/blacklist/'
SOLR_CRAWL_URL = 'http://localhost:8983/solr/crawler/'

class SolrPipeline(object):
    solr_crawl = pysolr.Solr(SOLR_CRAWL_URL, timeout=10)
    solr_blacklist = pysolr.Solr(SOLR_BLACKLIST_URL, timeout=10)

    def process_item(self, item, spider):
        # If only 3 fields, just update the Solr record
        if len(item) == 3:
            self.solr_crawl.add([item], fieldUpdates={'js_contents': 'set'})
        # Otherwise, perform blacklist lookup before inserting the item into Solr core
        else:
            # Check if any URL is in the blacklists
            query = 'url:({0})'.format(' OR '.join(urls))
            results = self.solr_blacklist.search(q=query, rows=0)

            # Update the item with the result
            item['blacklist_count'] = results.hits

            self.solr_crawl.add([item])

        return item
