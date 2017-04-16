'''
    Extracts data from a given results .json file

    The goal of this script is to extract N website results
    and summarize their data for insertion into a database (e.g., Solr).
'''
import os, re, sys, json
from datetime import datetime

import pysolr
from bs4 import BeautifulSoup

from blacklist_check import parse_url, LookupTable, CrawlIndex, DAYS_CRAWLED

CRAWL_DATA_DIR = '/home/crawler/mlcrawler6262/crawler/crawler-scrapy/alexatop/data/'

# Number of Alexa URLs per data file
RANK_DELTA = 100000
RANK_MAX = 1000000

# Data for blacklists by day
BLACKLIST_DIR = '/home/crawler/mlcrawler6262/crawler/blacklist'
BLACKLIST_FILE = os.path.join(BLACKLIST_DIR, 'blacklist-{0}.csv')

# Data output directory
OUTPUT_DIR = 'output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Solr configuration
SOLR_CORE_URL = 'http://localhost:8983/solr/search/'
SOLR_DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

def format_date(dt, fmt=SOLR_DATE_FORMAT):
    return datetime.strftime(dt, fmt)

def blacklist_lookup(lookup_table, blacklist):
    '''
        Given a URL lookup table, checks which URLs are in the blacklist.

        Arguments
            - lookup_table: LookupTable instance
            - blacklist: list of URLs (string)

        Returns: list of [url, rank] in blacklist.
    '''
    found = []

    # Check if any crawled URLs are in the blacklist
    for each in blacklist:
        result = lookup_table.lookup(url)

        if result:
            found.append(result)

    return found

def load_blacklist(day):
    '''
        Load URL blacklist (in CSV format) for a given day (dd-mm-yy).

        Return: list of URLs in blacklist
    '''
    blacklist = []

    with open(BLACKLIST_FILE.format(day), 'r') as f:
        for line in f:
            url = line.split(',')[0]
            blacklist.append(url)

    # with open(BLACKLIST_FILE.format(day), 'r') as f:
    #     for line in f:
    #         url = line.split(',')[0]
    #         l = blacklist.get(url[:5], [])
    #         l.append(url)
    #         blacklist[url[:5]] = l

    return blacklist

def grab_ranks(day, ranks):
    '''
        Grab data samples for crawl for given day for specific ranks.

        Arguments
            - ranks: list of Alexa ranks (int)

        Returns: list of parsed JSON objects for all given ranks.
    '''
    crawl_index = CrawlIndex(day)
    crawl_index.load()

    if not crawl_index.loaded:
        print('No crawl index available for {0}!'.format(day))
        sys.exit(0)

    data = []

    for rank in ranks:
        # Retrieve data using crawl index
        r = crawl_index.get(rank)

        # Skip any ranks that have not been crawled
        if r:
            data.append(r)

    return data

def grab_rank_range(day, n=1, m=1000):
    '''
        Grab data samples from crawl data for a given day from rank `n` to `m` (inclusive).

        Arguments:
            - n: start rank (inclusive)
            - m: stop rank (inclusive)

        Returns: list of parsed JSON objects for the entire rank range.
    '''
    if n > m:
        return []

    crawl_index = CrawlIndex(day)
    crawl_index.load()

    if not crawl_index.loaded:
        print('No crawl index available for {0}!'.format(day))
        sys.exit(0)

    data = []

    for rank in range(n, m+1):
        r = crawl_index.get(rank)

        if r:
            data.append(r)

    return data

def parse_data(day, data, blacklisted=False):
    '''
        Parse data samples into a summarized format with features of interest.

        Arguments
            - day: day, in dd-mm-yy format
            - data: list of dicts of crawl data to parse
    '''
    # Grab blacklist for current day
    if not blacklisted:
        blacklist = load_blacklist(day)

    parsed = []

    # Reformat date into Solr standard format for querying
    date_solr = format_date(datetime.strptime(day, '%d-%m-%y'))

    for result in data:
        # Object to store fields required
        d = {
            'crawl_status': result['crawl_status'],
            'date': date_solr,
            'alexa_rank': result['alexa_rank']
        }

        # Store parsed URL
        d['url'] = url = parse_url(result['url'])

        if blacklisted:
            # Already in blacklist
            d['blacklisted'] = True
        else:
            d['blacklisted'] = False

            # Perform blacklist lookup
            for u in blacklist:
                if url == u:
                    d['blacklisted'] = True
                    break

        # Continue loop if not correctly crawled
        if d['crawl_status'] != 'OK':
            parsed.append(d)
            continue

        # Parse raw_html into BS object
        page = BeautifulSoup(result['full_html'], 'lxml')
        d['page_size'] = len(result['full_html'])

        # Get number of words
        body = page.select('body')[0]
        d['num_words'] = len(body.get_text().replace('\n', '').split(' '))

        # Get number of images
        d['num_images'] = len(page.select('img'))

        # Other parameters
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

        parsed.append(d)

    return parsed

def extract_data(day, n=1, m=1000):
    print('Grabbing data from rank {0} to rank {1}.'.format(n, m))
    data = grab_rank_range(day, n, m)

    print('Parsing the data...')
    parsed = parse_data(day, data)

    # Parse and write data to JSON file, one object per line
    output_file = os.path.join(OUTPUT_DIR, 'output-{0}-{1}-{2}.json'.format(day, n, m))
    with open(output_file, 'w') as f:
        for each in parsed:
            f.write(json.dumps(each) + '\n')

    print('Data written to: ' + output_file)

def extract_blacklist_data(day):
    # Find which crawled URLs are in the blacklist for given day
    print('Performing blacklist lookups...')
    blacklist = load_blacklist(day)
    lookup_table = LookupTable(day)
    hits = blacklist_lookup(lookup_table, blacklist)

    # Extract the ranks and retrieve data
    ranks = [pair[1] for pair in hits]
    print('Grabbing data for {0} different ranks.'.format(len(ranks)))
    data = grab_ranks(day, ranks)

    # Finally, parse the data into summarized form
    print('Parsing the data...')
    parsed = parse_data(day, data, blacklisted=True)

    # Write results to output file for given day
    output_file = os.path.join(OUTPUT_DIR, 'output-{0}-blacklist.json'.format(day))
    with open(output_file, 'w') as f:
        for each in parsed:
            f.write(json.dumps(each) + '\n')

    print('Data written to: ' + output_file)

def main():
    # First 1000
    extract_data('15-04-17', n=1, m=1000)

    # Last 1000
    extract_data('15-04-17', n=999001, m=1000000)

    # Blacklisted
    #extract_blacklist_data('13-04-17')

if __name__ == '__main__':
    main()
