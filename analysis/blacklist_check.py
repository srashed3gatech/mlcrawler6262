import os
import re
import json
import pickle
import subprocess

import pandas as pd

DAYS_CRAWLED = [
    '04-04-17',
#    '05-04-17',
    '06-04-17',
    '07-04-17',
    '11-04-17',
    '12-04-17',
    '13-04-17',
    '14-04-17',
    '15-04-17',
    # '16-04-17',
]

# Directory that contains crawled JSON lines from Scrapy
# 10 files per day, each with results from 100k crawled URLs
CRAWL_DATA_DIR = '/home/crawler/mlcrawler6262/crawler/crawler-scrapy/alexatop/data'

# Number of Alexa URLs per data file
RANK_DELTA = 100000
RANK_MAX = 1000000

'''
Extracts TLD info from URL
  - Parses http(s) with and without www
    - Parses >2 / as well!
  - Skips any trailing paths
  - Skips any escaped characters in the URL (e.g, %5C)
'''
URL_REGEX = re.compile(r'https?:[/]+(www\.)?([^/%\?]+)')

# Data for blacklists by day
BLACKLIST_DIR = '/home/crawler/mlcrawler6262/crawler/blacklist'
BLACKLIST_FILE = os.path.join(BLACKLIST_DIR, 'blacklist-{0}.csv')
BLACKLIST_REGEX = re.compile(r'(www.)?(\S+)')

# Location of lookup table pickle for day {0}
LOOKUP_DIR = '/home/crawler/mlcrawler6262/analysis/lookup'
os.makedirs(LOOKUP_DIR, exist_ok=True)
LOOKUP_TABLE = os.path.join(LOOKUP_DIR, 'urls-{0}')

def parse_url(url, p=URL_REGEX):
    return re.search(p, url).group(2)

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

def load_lookup_table(day):
    path = LOOKUP_TABLE.format(day)

    if os.path.exists(path):
        with open(path, 'rb') as f:
            urls = pickle.load(f)
    else:
        return None

def build_lookup_table(day):
    '''
        Given a day, extract all crawled URLs from the day and store in a pickle.

        Return: True on success, False on failure
    '''
    # If already exists, return
    if os.path.exists(LOOKUP_TABLE.format(day)):
        return True

    # Get all crawl JSON files for day
    files = sorted([each for each in os.listdir(CRAWL_DATA_DIR) if day in each])

    if len(files) > RANK_MAX / RANK_DELTA:
        return False

    # Extract URLs from crawled data for day 2

    # Build a hash-based lookup table
    # Key: first 5 chars of URL, Value: list of URLs
    crawled = {}

    # Track rank offset of current data file
    rank_offset = 0

    for i, each in enumerate(files):
        path = os.path.join(CRAWL_DATA_DIR, each)

        with open(path, 'r') as f:
            for line in f:
                # Parse each line into a JSON object
                r = json.loads(line, encoding='utf-8')

                try:
                    # Extract URL using regex
                    url = re.search(URL_REGEX, r['url']).group(2)

                    # Store URL in lookup table
                    # Note: table WILL have dupes (e.g., YouTube)
                    # Kept them to maintain rank data
                    lookup = crawled.get(url[:5], [])
                    lookup.append([url, r['alexa_rank'] + rank_offset])
                    crawled[url[:5]] = lookup
                except:
                    # Skips malformed URLs
                    pass

        rank_offset += RANK_DELTA

        print('Completed file ' + str(i+1))

    # Save lookup table for later use
    with open(LOOKUP_TABLE.format(day), 'wb') as f:
        pickle.dump(crawled, f)

    return True

def check_blacklist(day1, day2):
    '''Given two days, computes blacklist diff, then checks diff against day 2 URLs.'''
    # Compute diff in blacklists
    blacklist = blacklist_diff(day1, day2)
    # path = BLACKLIST_FILE.format(day2)
    # blacklist = list(pd.read_csv(path, header=None)[0])

    # Retrieve URL lookup table for day 2
    path = LOOKUP_TABLE.format(day2)

    # Build table from scratch if doesn't exist (takes time!)
    if not os.path.exists(path):
        status = build_lookup_table(day2)
        if not status:
            print('URL lookup failed!')
            return

    # Load lookup table from disk
    urls = load_lookup_table(day2)

    blacklisted = []

    # Check for blacklist hits
    for each in blacklist:
        # Extract correct URL format
        url = re.search(BLACKLIST_REGEX, each).group(2)

        # Perform lookup in crawled URLs
        # Returns: [[<url>, <rank>], [<url>, <rank>], ...]
        options = urls.get(url[:5], [])

        for pair in options:
            if pair[0] == url:
                blacklisted.append((url, rank))
                break

    for url, rank in blacklisted:
        print('Found: {0} at rank {1}'.format(url, rank))

def main():
    # check_blacklist('12-04-17', '13-04-17')

    # Start from most recent data backwards
    days = DAYS_CRAWLED[::-1]

    for i, day in enumerate(days):
        if i == len(DAYS_CRAWLED)-1:
            break

        day1, day2 = days[i+1], day

        check_blacklist(day1, day2)

if __name__ == '__main__':
    main()
