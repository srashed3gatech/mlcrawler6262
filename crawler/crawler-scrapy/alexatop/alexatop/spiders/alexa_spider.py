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
CRAWL_NUM = 250000

class AlexaSpider(scrapy.Spider):
    name = 'alexa'

    def start_requests(self):
        urls = [v for v in list(grab_alexa(CRAWL_NUM).values())]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse,
                                 errback=self.req_error)

    def req_error(self, failure):
        # http://stackoverflow.com/questions/31146046/how-do-i-catch-errors-with-scrapy-so-i-can-do-something-when-i-get-user-timeout
        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error('HttpError for {}'.format(response.url))
        elif failure.check(DNSLookupError):
            request = failure.request
            self.logger.error('DNSLookupError for {}'.format(request.url))
        elif failure.check(TimeoutError):
            request = failure.request
            self.logger.error('TimeoutError for {}'.format(request.url))
        else:
            self.logger.error(repr(failure))

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
        pk = compute_md5('{0}{1}'.format(url, datetime.date.today()))

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
        # TODO: crawl the linked JS and hash it?
        js_urls = [{"numberOfJS":len(response.xpath('//script/@src').extract())}]

        # Extract other info from page
        title = response.xpath('/html/head/title/text()').extract_first()
        headers = dict_to_json(response.headers)
        latency = response.meta['download_latency']

        item = AlexaItem(
            url=url,
            timestamp=timestamp,
            pk=pk,
            full_hash=full_hash,
            body_hash=body_hash,
            head_hash=head_hash,
            urls=urls,
            urls_hash=urls_hash,
            js_urls=js_urls,
            title=title,
            headers=headers,
            latency=latency,
        )

        if len(response.xpath('//script/@src')) > 0:
            for jsurl in response.xpath('//script/@src').extract():
                request = scrapy.Request(response.urljoin(jsurl), callback=self.jsParser)
                request.meta['item'] = {'js_urls':item['js_urls'], 'pk':item['pk']}
                yield request
        yield item;

    def jsParser(self, response):
        item = response.meta['item']
        item['js_urls'] = {response.url:response.body}
        yield item
