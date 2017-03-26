import scrapy
from ..items import TutorialItem
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TimeoutError
import hashlib
import random
import time
import json


class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def start_requests(self):
        urls = [
            'https://superuser.com/questions/799464/how-does-a-web-browser-know-if-destination-is-http-or-https'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={'bindadderss':self})

    def parse(self, response):

        # Compute a "unique" primary key for Solr indexing
        url = response.url
        timestamp = time.time()
        pk = self.compute_md5(url)

        # Compute MD5 hashes of page sections
        full = response.xpath('/html').extract_first()
        full_hash = self.compute_md5(full)

        body = response.xpath('/html/body').extract_first()
        body_hash = self.compute_md5(body)

        head = response.xpath('/html/head').extract_first()
        head_hash = self.compute_md5(head)

        # Extract ALL valid urls from page
        urls = [url for url in response.xpath('//a/@href').extract() if 'http' in url]
        urls_hash = self.compute_md5(''.join(urls))

        # Extract JS links - will get in below and send as separate solr add
        # TODO: crawl the linked JS and hash it?
        if len(response.xpath('//script/@src').extract()) > 0 :
            js_urls =  response.xpath('//script/@src').extract()
            js_contents = ["NO_DATA"] * len(js_urls) #fixed size
        else:
            js_urls = []
            js_contents = []

        print(js_urls)
        print(js_contents)
        # Extract other info from page
        title = response.xpath('/html/head/title/text()').extract_first()
        headers = self.dict_to_json(response.headers)
        latency = response.meta['download_latency']

        item = TutorialItem(
            url=url,
            timestamp=timestamp,
            pk=pk,
            full_html = full,
            full_hash=full_hash,
            body_hash=body_hash,
            head_hash=head_hash,
            urls=urls,
            urls_hash=urls_hash,
            js_urls=js_urls,
            js_contents = js_contents,
            title=title,
            headers=headers,
            latency=latency,
            blacklist_count=0 #we'll get value on pipelines
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
        print(item_index)
        yield item

    def compute_md5(self,s):
        return hashlib.md5(s.encode('utf-8')).hexdigest()

    def dict_to_json(self, d):
        '''Convert a dict to JSON.'''
        # Convert a binary dict to clean dict for JSON encoding
        # http://stackoverflow.com/questions/33137741/fastest-way-to-convert-a-dicts-keys-values-from-bytes-to-str-in-python3
        def convert(data):
            if isinstance(data, list):   return data[0].decode()
            if isinstance(data, bytes):  return data.decode()
            if isinstance(data, dict):   return dict(map(convert, data.items()))
            if isinstance(data, tuple):  return map(convert, data)
            return data

        return json.dumps(convert(d))
