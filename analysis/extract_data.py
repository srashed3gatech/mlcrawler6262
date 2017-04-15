'''
    Extracts data from a given results .json file

    The goal of this script is to extract N website results
    and summarize their data for insertion into a database (e.g., Solr).
'''
import os
import json
import pysolr
from bs4 import BeautifulSoup
from datetime import datetime

from blacklist_check import parse_url, BLACKLIST_FILE

CRAWL_DATA_DIR = '/home/crawler/mlcrawler6262/crawler/crawler-scrapy/alexatop/data/'

OUTPUT_DIR = 'output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

SOLR_CORE_URL = 'http://localhost:8983/solr/search/'
SOLR_DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

def format_date(dt, fmt=SOLR_DATE_FORMAT):
    return datetime.strftime(dt, fmt)

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

def parse_data(day, data):
    '''Parse data samples into a summarized format with information of interest.'''
    # Grab blacklist for current day
    blacklist = load_blacklist(day)

    # Stores final parsed data
    parsed = []

    # Reformat date into Solr standard format for querying
    date_solr = format_date(datetime.strptime(day, '%d-%m-%y'))

    for result in data:
        # Object to store fields required
        d = {}

        # Store parsed URL and date
        d['url'] = url = parse_url(result['url'])
        d['date'] = date_solr

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
        # d['headers'] = json.loads(result['headers'])
        d['headers_length'] = len(result['headers'])

        d['head_hash'] = result['head_hash']
        d['urls_hash'] = result['urls_hash']
        d['body_hash'] = result['body_hash']

        if result['title']:
            d['title'] = result['title'].strip()
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

def extract_data(day, n=1000, solr=False):
    data = grab_data(day, n)
    parsed = parse_data(day, data)

    if not solr:
        # Write to JSON file
        output_file = os.path.join(OUTPUT_DIR, 'output-{0}.json'.format(day))

        with open(output_file, 'w') as f:
            json.dump(parsed, f)

        print('Data written to: ' + output_file)
    else:
        # Insert directly into Solr core `search`
        core = pysolr.Solr(SOLR_CORE_URL, timeout=10)
        core.add(parsed)

        print('Data inserted into: ' + SOLR_CORE_URL)

def main():
    extract_data('13-04-17', n=1000, solr=False)
    extract_data('12-04-17', n=1000, solr=False)

if __name__ == '__main__':
    main()
