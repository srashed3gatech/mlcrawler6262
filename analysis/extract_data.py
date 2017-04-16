'''
    Extracts data from a given results .json file

    The goal of this script is to extract N website results
    and summarize their data for insertion into a database (e.g., Solr).
'''
import os, re, sys, json
from datetime import datetime

import pysolr
from bs4 import BeautifulSoup

from blacklist_check import parse_url, load_lookup_table, DAYS_CRAWLED

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

def blacklist_lookup(urls, blacklist):
    '''
        Given a URL lookup table, checks which URLs are in the blacklist.

        Arguments
            - urls: dict of {first 5 chars of URL: list of (url, rank)}
            - blacklist: list of URLs

        Returns: list of (url, rank) in blacklist
    '''
    found = []

    # Check if any crawled URLs are in the blacklist
    for each in blacklist:
        # Extract correct URL format
        url = re.search(BLACKLIST_REGEX, each).group(2)

        # Perform lookup in crawled URLs
        # Returns: [[<url>, <rank>], [<url>, <rank>], ...]
        options = urls.get(url[:5], [])

        for pair in options:
            if pair[0] == url:
                found.append((url, rank))
                break

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
    '''
    # Grab all files crawled for the day (in order of name)
    files = sorted([each for each in os.listdir(CRAWL_DATA_DIR) if day in each])

    if len(files) != 10:
        print('Incorrectly crawled data for day {0}.'.format(day))
        sys.exit(0)

    data = []

    # Track iterations since last found rank, used to terminate early
    last_found = 0

    # Loop over start ranks of each file
    # (1, 1+RANK_DELTA, 2+RANK_DELTA, ..., RANK_MAX-RANK_DELTA)
    for i, offset in enumerate(range(0, RANK_MAX, RANK_DELTA)):
        # Retrieve ranks that are in this file
        current_ranks = []
        for r in sorted(set(ranks)):
            if offset < r <= offset + RANK_DELTA:
                current_ranks.append(r)

        # Skip this file if no ranks of interest
        if not current_ranks:
            continue

        # Iterate through current file
        with open(os.path.join(CRAWL_DATA_DIR, files[i]), 'r') as f:
            for line in f:
                # If current_ranks empty, stop
                if not current_ranks or last_found >= 3000:
                    break

                r = json.loads(line, encoding='utf-8')

                # Rank correction done b/c of per-file rank info
                r['alexa_rank'] += offset

                if r['alexa_rank'] in current_ranks:
                    data.append(r)
                    current_ranks.remove(r['alexa_rank'])
                    last_found = 0
                else:
                    last_found += 1

    return data

def grab_rank_range(day, n=1, m=1000):
    '''
        Grab data samples from crawl data for a given day from rank `n` to `m` (inclusive).

        Note: n, m must both be within the bounds of a single file.
    '''
    if n > m:
        return []

    # Grab all files crawled for the day
    files = sorted([each for each in os.listdir(CRAWL_DATA_DIR) if day in each])

    if len(files) != 10:
        print('Incorrectly crawled data for day {0}.'.format(day))
        sys.exit(0)

    data = []

    # Track iterations since last found rank, used to terminate early
    last_found = 0

    # Loop over start ranks of each file
    # (1, 1+RANK_DELTA, 2+RANK_DELTA, ..., RANK_MAX-RANK_DELTA)
    for i, offset in enumerate(range(0, RANK_MAX, RANK_DELTA)):
        # Start processing file iff it contains rank range
        if offset < n and m <= offset + RANK_DELTA:
            with open(os.path.join(CRAWL_DATA_DIR, files[i]), 'r') as f:
                for line in f:
                    # Stop once all results crawled
                    # Or terminate if 3000 iterations since last "hit"
                    if len(data) == m-(n-1) or last_found >= 3000:
                        break

                    # Parse line into JSON
                    r = json.loads(line, encoding='utf-8')

                    # Correction using offset done b/c data crawled with per-file rank info!
                    r['alexa_rank'] += offset

                    # Note: result *may* be incorrectly crawled!
                    # Save results in the range specified
                    if n <= r['alexa_rank'] <= m:
                        data.append(r)
                        last_found = 0
                    elif r['alexa_rank'] >= n:
                        last_found += 1
            break

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
        # num_images = len(re.findall(r'<img([\w\W]+?)/?>', result['full_html']))

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
    urls = load_lookup_table(day)
    hits = blacklist_lookup(urls, blacklist)

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
    #extract_data('13-04-17', n=999001, m=1000000)

    # Blacklisted
    #extract_blacklist_data('13-04-17')

if __name__ == '__main__':
    main()
