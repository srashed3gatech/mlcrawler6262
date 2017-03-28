# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pysolr

from .util import *

SOLR_BLACKLIST_URL = 'http://localhost:8983/solr/blacklist/'
SOLR_CRAWL_URL = 'http://localhost:8983/solr/crawler/'

class SolrPipeline(object):
    solr_crawl = pysolr.Solr(SOLR_CRAWL_URL, timeout=10)
    solr_blacklist = pysolr.Solr(SOLR_BLACKLIST_URL, timeout=10)

    def process_item(self, item, spider):
        item = dict(item)
        item['id'] = item['pk']

        # If only 3 fields, just update the Solr record
        if len(item) == 3:
            self.solr_crawl.add([item], fieldUpdates={'js_contents': 'set'})
        # Otherwise, perform blacklist lookup before inserting the item into Solr core
        else:
            # Check if any URL is in the blacklists
            if item['crawl_status'] == 'OK':
                # First, check if any JS URL points to blacklisted site
                js_urls = {extract_url(url) for url in item['js_urls']}

                if len(js_urls) > 0:
                    query = 'url:({0})'.format(' OR '.join(js_urls))
                    results = self.solr_blacklist.search(q=query, rows=0)
                    item['num_js_blacklist'] = results.hits
                else:
                    item['num_js_blacklist'] = 0

                # Next, check for just linked URLs in the blacklist
                urls = set(item['urls'])
                if len(urls) > 0:
                    query = 'url:({0})'.format(' OR '.join(urls))
                    results = self.solr_blacklist.search(q=query, rows=0)
                    item['num_blacklist'] = results.hits
                else:
                    item['num_blacklist'] = 0

            self.solr_crawl.add([item])

        return item
