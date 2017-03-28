from ..items import AlexaItem
from ..util import *

import scrapy
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TimeoutError

import random
import re
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
        crawl_status = None

        if failure.check(HttpError):
            crawl_status = 'HTTPError'
            self.logger.error(crawl_status)
        elif failure.check(DNSLookupError):
            crawl_status = 'DNSLookupError'
            self.logger.error(crawl_status)
        elif failure.check(TimeoutError):
            crawl_status = 'TimeoutError for {}'.format(request.url)
            self.logger.error(crawl_status)
        else:
            crawl_status = repr(failure)
            self.logger.error(repr(failure))

        request = failure.request
        url = request.url
        timestamp = time.time()
        pk = compute_md5('{0}{1}'.format(url, TODAY))

        item = AlexaItem(
            url=url,
            timestamp=timestamp,
            crawl_status=crawl_status,
            alexa_rank=failure.request.meta['rank']
        )

        item['id'] = pk

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
        page_url = response.url
        timestamp = time.time()
        pk = compute_md5('{0}{1}'.format(url, TODAY))

        # Compute MD5 hashes of page sections
        full = response.xpath('/html').extract_first()
        full_hash = compute_md5(full)

        body = response.xpath('/html/body').extract_first()
        body_hash = compute_md5(body)

        head = response.xpath('/html/head').extract_first()
        head_hash = compute_md5(head)

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

        # TODO: Extract JS content from <script></script> elements?

        # Allocate entries for JS contents
        js_contents = ['N' for url in js_urls]

        # Extract other info from page
        title = response.xpath('/html/head/title/text()').extract_first()
        headers = dict_to_json(response.headers)
        latency = response.meta['download_latency']
        rank = response.meta['rank']
        crawl_status = 'OK'

        item = AlexaItem(
            url=page_url,
            timestamp=timestamp,
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
            alexa_rank = rank,
            crawl_status = crawl_status
        )

        item['id'] = pk

        # Generate requests to pull all linked JS on the page
        for i, url in enumerate(js_urls):
            request = scrapy.Request(response.urljoin(url), callback=self.parse_js)
            request.meta['data'] = {
                'id': item['id'],
                'idx': i
            }

            # TODO: Skip large JS?

            yield request

        yield item

    def parse_js(self, response):
        data = response.meta['data']
        data['js_contents'] = response.body
        yield data
