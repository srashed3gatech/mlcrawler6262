import os
import re
import json
import pickle
import subprocess

import pandas as pd

DAYS_CRAWLED = (
    '02-04-17',
    '03-04-17',
    '04-04-17',
    '05-04-17',
    '06-04-17',
    '07-04-17',
    '11-04-17',
    '12-04-17',
    '13-04-17',
    '14-04-17',
    '15-04-17',
)

# Directory that contains crawled JSON lines from Scrapy
# 10 files per day, each with results from 100k crawled URLs
CRAWL_DATA_DIR = '/home/crawler/mlcrawler6262/crawler/crawler-scrapy/alexatop/data/'
URL_REGEX = re.compile(r'https?://(www\.)?(\S+)(/|$)')

# Data for blacklists by day
BLACKLIST_DIR = '/home/crawler/mlcrawler6262/crawler/blacklist'
BLACKLIST_FILE = os.path.join(BLACKLIST_DIR, 'blacklist-{0}.csv')

def blacklist_diff(day1, day2):
    '''Given two days, returns blacklist URLs in day2 that were not found in day1.'''
    f1 = BLACKLIST_FILE.format(day1)
    f2 = BLACKLIST_FILE.format(day2)

    d1 = pd.read_csv(f1, header=None)
    d2 = pd.read_csv(f2, header=None)

    # Compute intersection of blacklists
    # True if d2_i in d1, False otherwise
    inter = d2[0].isin(d1[0])
    results = inter[inter == False]

    return list(d2[0][results.keys()])

def check_blacklist(day1, day2):
    '''Given two days, computes blacklist diff, then checks diff against day 2 URLs.'''
    # Compute diff in blacklists
    blacklist = blacklist_diff(day1, day2)

    # Get all crawl JSON files for day 2
    files = [each for each in os.listdir(CRAWL_DATA_DIR) if day2 in each]

    # Extract URLs from crawled data for day 2

    # Build a hash-based lookup table
    # Key: first 5 chars of URL, Value: list of URLs
    crawled = {}

    for i, each in enumerate(files):
        path = os.path.join(CRAWL_DATA_DIR, each)

        with open(path, 'r') as f:
            # Parse each line into JSON object
            for line in f:
                r = json.loads(line, encoding='utf-8')

                try:
                    url = re.search(URL_REGEX, r['url']).group(3)
                except:
                    # Skip any malformed URLs
                    print(r['url'])

                # Store URL in lookup table
                lookup = crawled.get(url[:5], [])
                lookup.append(url)
                crawled[url[:5]] = lookup

        print('Completed file ' + str(i+1))

    # Save lookup table for later use!
    with open('urls-{0}'.format(day2), 'wb') as f:
        pickle.dump(crawled, f)

    # Check if any crawled URLs are in the blacklist
    for url in blacklist:
        options = crawled[url[:5]]
        if url in options:
            print('Found: ' + url)

def main():
    check_blacklist('11-04-17', '12-04-17')

if __name__ == '__main__':
    main()
