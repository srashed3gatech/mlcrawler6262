'''
    Extracts data from a given results .json file

    The goal of this script is to extract N website results
    and summarize their data for insertion into a database (e.g., Solr).
'''
import os
import json
import pysolr
from bs4 import BeautifulSoup

from blacklist_check import parse_url, BLACKLIST_FILE

CRAWL_DATA_DIR = '/home/crawler/mlcrawler6262/crawler/crawler-scrapy/alexatop/data/'

OUTPUT_DIR = 'output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_blacklist(day):
    '''Load URL blacklist for a given day. Return: lookup table of first 5 chars of URL.'''
    blacklist = {}

    with open(BLACKLIST_FILE.format(day), 'r') as f:
        for line in f:
            url = line.split(',')[0]
            l = blacklist.get(url[:5], [])
            l.append(url)
            blacklist[url[:5]] = l

    return blacklist

def grab_data(day, n):
    '''Grab `n` data samples from crawl data for a given day.'''
    data = []

    # Grab first file crawled for the day (top 100k)
    path = [each for each in sorted(os.listdir(CRAWL_DATA_DIR)) if day in each][0]

    i = 0

    with open(os.path.join(CRAWL_DATA_DIR, path), 'r') as f:
        for line in f:
            if i == n:
                break

            # Parse line into JSON
            r = json.loads(line, encoding='utf-8')

            # Only append correctly crawled pages
            if r['crawl_status'] == 'OK':
                data.append(r)
                i += 1

    return data

def parse_data(data, blacklist):
    '''Parse data samples into a summarized format with information of interest.'''
    # Extract:
    # page size (bytes), num images, num JS urls, avg. JS url length, num URLs
    # avg. URL length, num words in <body>, resp. time, header length, num DOM elems
    # blacklisted, Alexa rank

    parsed = []

    for result in data:
        # Object to store fields required
        d = {}

        d['url'] = url = parse_url(result['url'])

        # Parse raw_html into BS object
        page = BeautifulSoup(result['full_html'], 'lxml')
        d['page_size'] = len(result['full_html'])

        # Get number of words
        body = page.select('body')[0]
        d['num_words'] = len(body.get_text().replace('\n', '').split(' '))

        # Get number of images
        d['num_images'] = len(page.select('img'))

        # Other parameters
        d['alexa_rank'] = result['alexa_rank']

        d['num_urls'] = len(result['urls'])

        if d['num_urls'] > 0:
            d['avg_url_length'] = sum([len(url) for url in result['urls']]) / float(d['num_urls'])
        else:
            d['avg_url_length'] = 0

        d['num_js_urls'] = len(result['js_urls'])

        if d['num_js_urls'] > 0:
            d['avg_js_url_length'] = sum([len(url) for url in result['js_urls']]) / float(d['num_js_urls'])
        else:
            d['avg_js_url_length'] = 0

        # TODO: look at headers!
        d['latency'] = result['latency']
        d['headers'] = json.loads(result['headers'])
        d['headers_length'] = len(result['headers'])

        d['head_hash'] = result['head_hash']
        d['urls_hash'] = result['urls_hash']
        d['body_hash'] = result['body_hash']

        d['title'] = result['title'].strip()

        if d['title']:
            d['title_length'] = len(result['title'])
        else:
            d['title_length'] = 0

        d['blacklisted'] = False

        # Perform blacklist lookup
        if url[:5] in blacklist:
            if url in blacklist[url[:5]]:
                d['blacklisted'] = True

        parsed.append(d)

    return parsed

def extract_data(day, n=1000):
    output_file = os.path.join(OUTPUT_DIR, 'output-{0}.json'.format(day))

    data = grab_data(day, n)
    blacklist = load_blacklist(day)
    parsed = parse_data(data, blacklist)

    with open(output_file, 'w') as f:
        json.dump(parsed, f)

    print('Data written to: ' + output_file)

def main():
    extract_data('13-04-17', n=100)

if __name__ == '__main__':
    main()
