import scrapy
from ..items import BLItem
from ..util import *
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TimeoutError
import hashlib
import random
import time
import json
import pandas as pd
import os

#seed file Location
#SEED_FILE = "/home/crawler/mlcrawler6262/crawler/bl-crawler/seed/seed.csv"
SEED_FILE = "seed/seed.csv"
# Today's date, in Solr format
TODAY = get_today()
class BLSpider(scrapy.Spider):
    name = "blacklist"

    def start_requests(self):
        blackLists = pd.read_csv(SEED_FILE,names=['url','label'],header=None)
        for url,label in blackLists.values:
            yield scrapy.Request(url='http://'+url, callback=self.parse,
                                    errback=self.req_error,
                                    meta={'label':label})

    def req_error(self, failure):
        crawl_status = None

        if failure.check(HttpError):
            crawl_status = 'HTTPError'
            self.logger.error(crawl_status)
        elif failure.check(DNSLookupError):
            crawl_status = 'DNSLookupError'
            self.logger.error(crawl_status)
        elif failure.check(TimeoutError):
            crawl_status = 'TimeoutError for {}'.format(failure.request.url)
            self.logger.error(crawl_status)
        else:
            crawl_status = repr(failure)
            self.logger.error(repr(failure))

        url = failure.request.url
        pk = compute_md5('{0}{1}'.format(url, TODAY))
        label = failure.request.meta['label']
        item = BLItem(
            url=url,
            pk=pk,
            date=TODAY,
            crawl_status=crawl_status,
            label = label
        )

        yield item

    def parse(self, response):
        # Compute a "unique" primary key for Solr indexing
        page_url = response.url
        pk = compute_md5('{0}{1}'.format(page_url, TODAY))

        # Compute MD5 hashes of page sections
        full = response.xpath('/html').extract_first()
        body = response.xpath('/html/body').extract_first()
        head = response.xpath('/html/head').extract_first()

        # Stop crawling the page if it is invalid HTML
        if not (full and body and head):
            return BLItem(
                url=page_url,
                pk=pk,
                date=TODAY,
                crawl_status="ERROR: INVALID HTML"
            )

        full_hash = compute_md5(full)
        head_hash = compute_md5(head)
        body_hash = compute_md5(body)

        # Extract ALL valid urls from page; keep only domain, remove any pages
        urls_all = [url for url in response.xpath('//a/@href').extract() if 'http' in url]
        urls_set = set()

        for url in urls_all:
            parsed = extract_url(url)
            urls_set.add(parsed)

        urls = list(urls_set)
        urls_hash = compute_md5(''.join(urls))

        # Extract JS links from page
        js_urls = response.xpath('//script/@src').extract()

        # Extract other info from page
        title = response.xpath('/html/head/title/text()').extract_first()
        headers = dict_to_json(response.headers)
        latency = response.meta['download_latency']
        crawl_status = 'OK'
        label = response.meta['label']

        item = BLItem(
            url=page_url,
            title=title,
            pk=pk,
            date=TODAY,
            full_html = full,
            full_hash=full_hash,
            body_hash=body_hash,
            head_hash=head_hash,
            urls=urls,
            urls_hash=urls_hash,
            js_urls=js_urls,
            headers=headers,
            latency=latency,
            crawl_status = crawl_status,
            label = label
        )
        yield item
