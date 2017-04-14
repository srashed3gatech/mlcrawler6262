import os
import re
import json
import pickle
import subprocess

import pandas as pd

DAYS_CRAWLED = [
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
]

# Directory that contains crawled JSON lines from Scrapy
# 10 files per day, each with results from 100k crawled URLs
CRAWL_DATA_DIR = '/home/crawler/mlcrawler6262/crawler/crawler-scrapy/alexatop/data/'
URL_REGEX = re.compile(r'https?://(www\.)?(\S+)(/|$)')

# Data for blacklists by day
BLACKLIST_DIR = '/home/crawler/mlcrawler6262/crawler/blacklist'
BLACKLIST_FILE = os.path.join(BLACKLIST_DIR, 'blacklist-{0}.csv')
BLACKLIST_REGEX = re.compile(r'(www.)?(\S+)')

# Location of lookup table pickle for day {0}
LOOKUP_TABLE = '/home/crawler/mlcrawler6262/analysis/urls-{0}'

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

def build_lookup_table(day):
    '''Given a day, extract all crawled URLs from the day and store in a pickle.'''
    # Get all crawl JSON files for day
    files = [each for each in os.listdir(CRAWL_DATA_DIR) if day in each]

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
                    # Extract URL using regex
                    url = re.search(URL_REGEX, r['url']).group(2)

                    # Store URL in lookup table
                    lookup = crawled.get(url[:5], [])
                    lookup.append([url, r['alexa_rank']])
                    crawled[url[:5]] = lookup
                except:
                    # Skip any malformed URLs
                    print(r['url'])

        print('Completed file ' + str(i+1))

    # Save lookup table for later use
    with open(LOOKUP_TABLE.format(day), 'wb') as f:
        pickle.dump(crawled, f)

    return crawled

def check_blacklist(day1, day2):
    '''Given two days, computes blacklist diff, then checks diff against day 2 URLs.'''
    # Compute diff in blacklists
    blacklist = blacklist_diff(day1, day2)

    # Retrieve URL lookup table for day 2
    path = LOOKUP_TABLE.format(day2)

    if os.path.exists(path):
        # Read pickle if lookup table exists
        with open(path, 'rb') as f:
            urls = pickle.load(f)
    else:
        # Build table from scratch (takes time!)
        urls = build_lookup_table(day2)

    # Check if any crawled URLs are in the blacklist
    for each in blacklist:
        # Extract correct URL format
        url = re.search(BLACKLIST_REGEX, each).group(2)

        # Perform lookup in crawled URLs
        # Returns: [[<url>, <rank>], [<url>, <rank>], ...]
        options = urls.get(url[:5], [])

        for pair in options:
            if pair[0] in url:
                print('Found: ' + url)
                break

def main():
    check_blacklist('12-04-17', '13-04-17')

if __name__ == '__main__':
    main()
