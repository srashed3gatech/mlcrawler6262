import os
import re
import json
import pickle
import subprocess
from collections import OrderedDict

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

CRAWL_INDEX_DIR = '/home/crawler/mlcrawler6262/crawler/crawler-scrapy/alexatop/data/crawl_index'
os.makedirs(CRAWL_INDEX_DIR, exist_ok=True)
CRAWL_INDEX_PATH = os.path.join(CRAWL_INDEX_DIR, 'index-{0}')

CRAWL_STATS_DIR = '/home/crawler/mlcrawler6262/crawler/crawler-scrapy/alexatop/data/stats'
os.makedirs(CRAWL_STATS_DIR, exist_ok=True)
CRAWL_STATS_PATH = os.path.join(CRAWL_STATS_DIR, 'stats-{0}')

class StatsCollector:
    '''
        Collects statistics on crawled data for a given day.
    '''
    def __init__(self, day):
        self.day = day
        self.path = CRAWL_STATS_PATH.format(day)
        self.stats = OrderedDict([
            ('total_crawled', 0),
            ('dns_fail', 0),
            ('http_fail', 0),
            ('http_timeout', 0),
            ('other_fail', 0),
            ('total_error', 0),
            ('total_ok', 0),
        ])

    def update(self, crawl_status):
        self.stats['total_crawled'] += 1

        if crawl_status == 'DNSLookupError':
            self.stats['dns_fail'] += 1
        elif crawl_status == 'HTTPError':
            self.stats['http_fail'] += 1
        elif 'TimeoutError' in crawl_status:
            self.stats['http_timeout'] += 1
        elif crawl_status == 'OK':
            self.stats['total_ok'] += 1
        else:
            self.stats['other_fail'] += 1

    def dump(self):
        with open(self.path, 'w') as f:
            # CSV header row
            f.write('{0}\n'.format(','.join(self.stats.keys())))

            # Stats for file
            self.stats['total_error'] = self.stats['dns_fail'] + self.stats['http_fail'] + \
                                        self.stats['http_timeout'] + self.stats['other_fail']
            stats_row = ','.join(self.stats.values())
            f.write('{0}\n'.format(stats_row))

class LookupTable:
    '''
        Builds and stores a lookup table for crawled URLs for a given day.

        Params: day (dd-mm-yy), idx (int): number of chars of URL to index
    '''
    def __init__(self, day, idx=5):
        self.day = day
        self.idx = idx
        self.path = LOOKUP_TABLE.format(self.day)
        self.table = {}

    def lookup(self, url):
        results = self.table.get(url[:self.idx], [])

        if results:
            for u, rank in results:
                if u == url:
                    return [url, rank]

        return []

    def insert(self, url, rank):
        '''Insert an entry into the table.'''
        lookup = self.table.get(url[:self.idx], [])
        lookup.append([url, rank])
        self.table[url[:self.idx]] = lookup

    def dump(self):
        '''Dumps lookup table to disk.'''
        with open(self.path, 'wb') as f:
            pickle.dump(f)

    def load(self):
        '''Loads lookup table from disk.'''
        if os.path.exists(self.path):
            with open(self.path, 'rb') as f:
                self.table = pickle.load(f)
        else:
            self.table = {}

class CrawlIndex:
    '''
        Builds a rank index for a given day.

        Given a rank, stores the path and seekpos in the index.
    '''
    def __init__(self, day):
        self.day = day
        self.path = CRAWL_INDEX_PATH.format(day)
        self.index = {}

    def insert(self, rank, path, seekpos):
        self.index[rank] = [path, seekpos]

    def lookup(self, rank):
        '''Return data for particular rank.'''
        path, seekpos = self.index.get(rank, [])

        if result:
            with open(path, 'r') as f:
                f.seek(seekpos)
                line = f.readline().strip()
                return json.parses(line)

        return {}

    def dump(self):
        with open(self.path, 'wb') as f:
            pickle.dump(f)

    def load(self):
        '''Loads index from disk.'''
        if os.path.exists(self.path):
            with open(self.path, 'rb') as f:
                self.index = pickle.load(f)
        else:
            self.index = {}

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
            return urls
    else:
        return None

def build_lookup_table(day):
    '''
        Given a day, extract all crawled URLs from the day and store in a pickle.

        Return: True on success, False on failure
    '''
    # If already exists, return
    # if os.path.exists(LOOKUP_TABLE.format(day)):
    #     return True

    # Get all crawl JSON files for day
    files = sorted([each for each in os.listdir(CRAWL_DATA_DIR) if day in each])

    if len(files) > RANK_MAX / RANK_DELTA:
        return False

    # Extract URLs from crawled data for day 2

    # Build a hash-based lookup table
    # Key: first 5 chars of URL, Value: list of URLs
    # crawled = {}

    # Track rank offset of current data file
    rank_offset = 0

    lookup_table = LookupTable(day)
    crawl_index = CrawlIndex(day)
    stats = StatsCollector(day)

    for i, each in enumerate(files):
        path = os.path.join(CRAWL_DATA_DIR, each)

        # Tracks seek position in current file
        seek_offset = 0

        with open(path, 'r') as f:
            for line in f:
                # Parse each line into a JSON object
                r = json.loads(line, encoding='utf-8')

                # Update crawl stats
                stats.update(r['crawl_status'])

                # Get full Alexa rank
                true_rank = r['alexa_rank'] + rank_offset

                # Insert seek data, and update seek position
                crawl_index.insert(true_rank, path, seek_offset)
                seek_offset += len(line)

                try:
                    # Extract URL using regex
                    url = re.search(URL_REGEX, r['url']).group(2)

                    # Store URL in lookup table
                    # Note: table WILL have dupes (e.g., YouTube)
                    # Kept them to maintain rank data
                    lookup_table.insert(url, true_rank)
                    # lookup = crawled.get(url[:5], [])
                    # lookup.append([url, r['alexa_rank'] + rank_offset])
                    # crawled[url[:5]] = lookup
                except:
                    # Skips malformed URLs
                    pass

        rank_offset += RANK_DELTA

        print('Completed file ' + str(i+1))

    # Save lookup table for later use
    # with open(LOOKUP_TABLE.format(day), 'wb') as f:
    #     pickle.dump(crawled, f)

    # Dump lookup table and crawl index
    lookup_table.dump()
    crawl_index.dump()
    stats.dump()

    return True

def check_blacklist(day1, day2):
    '''Given two days, computes blacklist diff, then checks diff against day 2 URLs.'''
    # Compute diff in blacklists
    blacklist = blacklist_diff(day1, day2)
    # path = BLACKLIST_FILE.format(day2)
    # blacklist = list(pd.read_csv(path, header=None)[0])

    # Load lookup table from disk
    urls = load_lookup_table(day2)

    # Build table from scratch if doesn't exist (takes time!)
    if not urls:
        status = build_lookup_table(day2)

        if not status:
            print('URL lookup failed!')
            return

        urls = load_lookup_table(day2)

    blacklisted = set()

    # Check for blacklist hits
    for each in blacklist:
        # Extract correct URL format
        url = re.search(BLACKLIST_REGEX, each).group(2)

        # Perform lookup in crawled URLs
        # Returns: [[<url>, <rank>], [<url>, <rank>], ...]
        options = urls.get(url[:5], [])

        for u, rank in options:
            if u == url:
                blacklisted.add((url, rank))
                break

    for url, rank in blacklisted:
        print('Found: {0} at rank {1}'.format(url, rank))

def main():
    build_lookup_table('15-04-17')

    # Start from most recent data backwards
    # days = DAYS_CRAWLED[::-1]
    #
    # for i, day in enumerate(days):
    #     if i == len(DAYS_CRAWLED)-1:
    #         break
    #
    #     day1, day2 = days[i+1], day
    #     print('Days: {0} vs. {1}'.format(day2, day1))
    #
    #     check_blacklist(day1, day2)

if __name__ == '__main__':
    main()
