from ..items import AlexaItem
from ..util import *

import scrapy
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TimeoutError

import random
import time
import datetime

# 1. Grab Alex top 1M list from source
# 2. Extract archive
# 3. Parse the csv and extract the URLs
# 4. Start crawling

# Number of Alexa sites to crawl
CRAWL_NUM = 200000
STARTIDX = 50000-1
TODAY = datetime.datetime.today().date()

class AlexaSpider(scrapy.Spider):
    name = 'alexa'

    def start_requests(self):
        for i, url in grab_alexa(CRAWL_NUM,STARTIDX).items():
            req = scrapy.Request(url=url, callback=self.parse,
                                 errback=self.req_error)
            req.meta['rank'] = i
            yield req

    def req_error(self, failure):
        # http://stackoverflow.com/questions/31146046/how-do-i-catch-errors-with-scrapy-so-i-can-do-something-when-i-get-user-timeout
        crawl_status = ""
        if failure.check(HttpError):
            response = failure.value.response
            crawl_status = 'HttpError for {}'.format(response.url)
            self.logger.error(crawl_status)
        elif failure.check(DNSLookupError):
            request = failure.request
            crawl_status = 'DNSLookupError for {}'.format(request.url)
            self.logger.error(crawl_status)
        elif failure.check(TimeoutError):
            request = failure.request
            crawl_status = 'TimeoutError for {}'.format(request.url)
            self.logger.error(crawl_status)
        else:
            crawl_status = repr(failure)
            self.logger.error(repr(failure))

        url = failure.request.url
        timestamp = time.time()
        pk = compute_md5('{0}{1}'.format(url, TODAY))
        item = AlexaItem(
            url=url,
            pk=pk,
            timestamp=timestamp,
            crawl_status=crawl_status,
            alexa_rank=failure.request.meta['rank']
        )
        yield item

    def parse(self, response):
        '''
            To extract:

            - id: hash of URL + timestamp
            - gzip compressed page
            - Hash of page
            - Hash of particular sections also?
            - Page title
            - Social media links (Twitter, FB, Instagram, YouTube)
            - CDN provider
            - CSS framework info (e.g., Bootstrap) (or not?)
            - Common JS includes (JQ, React, Flux, etc.)
            - Footer information (author, company, framework/CMS)
            - Ad providers + provider IDs (revenue stream)
            - Google Analytics ID
        '''
        # Compute a "unique" primary key for Solr indexing
        url = response.url
        timestamp = time.time()
        pk = compute_md5('{0}{1}'.format(url, TODAY))

        # Compute MD5 hashes of page sections
        full = response.xpath('/html').extract_first()
        full_hash = compute_md5(full)

        body = response.xpath('/html/body').extract_first()
        body_hash = compute_md5(body)

        head = response.xpath('/html/head').extract_first()
        head_hash = compute_md5(head)

        # Extract ALL valid urls from page
        urls = [url for url in response.xpath('//a/@href').extract() if 'http' in url]
        urls_hash = compute_md5(''.join(urls))

        # Extract JS links
        if len(response.xpath('//script/@src').extract()) > 0 :
            js_urls =  response.xpath('//script/@src').extract()
            js_contents = ["NO_DATA"] * len(js_urls) #fixed size
        else:
            js_urls = []
            js_contents = []

        # Extract other info from page
        title = response.xpath('/html/head/title/text()').extract_first()
        headers = dict_to_json(response.headers)
        latency = response.meta['download_latency']
        rank = response.meta['rank']
        crawl_status = "OK"

        item = AlexaItem(
            url=url,
            timestamp=timestamp,
            pk=pk,
            title=title,
            full_html = full,
            full_hash=full_hash,
            body_hash=body_hash,
            head_hash=head_hash,
            urls=urls,
            urls_hash=urls_hash,
            js_urls=js_urls,
            js_contents = js_contents,
            headers=headers,
            latency=latency,
            blacklist_count=0, #we'll get value on pipelines
            alexa_rank = rank,
            crawl_status = crawl_status
        )

        if len(js_urls) > 0:
            for jsurl in js_urls:
                request = scrapy.Request(response.urljoin(jsurl), callback=self.jsParser)
                request.meta['item'] = {'js_contents':item['js_contents'], 'pk':item['pk']}
                request.meta['item_index'] = js_urls.index(jsurl)
                yield request
        yield item;

    def jsParser(self, response):
        item = response.meta['item']
        item_index = response.meta['item_index']
        item['js_contents'][item_index] = response.body
        yield item
