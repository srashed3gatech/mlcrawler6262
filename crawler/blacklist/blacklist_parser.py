import re
import json
from hashlib import md5
from datetime import datetime

import requests

'''
    Formats:
        - hosts: HOSTS file format (127.0.0.1 -> URL)
        - malwaredomains: see regexes
        - url: one URL per line
'''
FORMATS = ['hosts', 'malwaredomains', 'url']

REGEXES = {
    'hosts': re.compile(r'^\S+\s+(\S+)$'),
    'malwaredomains': re.compile(r'^(\S+)\s+(\S+)\s+(\S+)\s+(\S+)$'),
    'url': re.compile(r'^(\S+)$')
}

BLACKLIST_SOURCES = [
    {'url': 'https://hosts-file.net/psh.txt', 'format': 'hosts', 'type': 'phish'},
    {'url': 'https://hosts-file.net/exp.txt', 'format': 'hosts', 'type': 'exploit'},
    {'url': 'https://hosts-file.net/emd.txt', 'format': 'hosts', 'type': 'malware'},
    {'url': 'https://hosts-file.net/fsa.txt', 'format': 'hosts', 'type': 'fraud'},
    {'url': 'http://mirror2.malwaredomains.com/files/domains.txt', 'format': 'malwaredomains', 'type': 'all'},
    {'url': 'https://isc.sans.edu/feeds/suspiciousdomains_Medium.txt', 'format': 'url', 'type': 'all'},
]

SOLR_DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

def format_date(dt, fmt=SOLR_DATE_FORMAT):
    return datetime.strftime(dt, fmt)

TODAY = format_date(datetime.now())

class BlacklistParser:
    '''
        Parses a blacklist of a given format.

        Throws: Exception
    '''
    def __init__(self, lines, f):
        self.results = []
        self.format = f

        if self.format not in FORMATS:
            raise Exception('Invalid blacklist format!')

        for line in lines:
            result = self.line_parser(line)

            if result != None:
                self.results.append(result)

    def line_parser(self, line):
        # Skip comment and/or empty lines
        if '#' in line or line.strip() == '':
            return None

        try:
            # Compute regex on line based on format
            p = REGEXES[self.format]
            cleaned = line.replace('\t', ' ').rstrip()
            groups = re.findall(p, cleaned)[0]
        except:
            return None

        # Invalid line, skip it
        if len(groups) == 0:
            return None

        result = {}

        # Extract fields from regex output
        if self.format == 'hosts':
            result['url'] = groups.strip()
        elif self.format == 'malwaredomains':
            result['url'] = groups[0].strip()
            result['type'] = groups[1].strip()
            result['source'] = groups[2].strip()

            # Convert date to Python datetime, then re-format for Solr
            dt = datetime.strptime(groups[3].strip(), '%Y%M%d')
            result['date'] = format_date(dt)
        elif self.format == 'url':
            result['url'] = groups.strip()

        if self.format != 'malwaredomains':
            result['type'] = 'all'
            result['source'] = 'unknown'
            result['date'] = TODAY

        # Assign unique ID to each URL
        s = result['url'] + TODAY
        result['id'] = md5(s.encode('utf-8')).hexdigest()

        return result

def main():
    # Grab each of the blacklists and parse them
    for source in BLACKLIST_SOURCES:
        r = requests.get(source['url'])
        lines = r.text.split('\n')

        b = BlacklistParser(lines, source['format'])

        # Dump results into JSON file (append)
        with open('data.json', 'w+') as f:
            json.dump(b.results, f)

        print('- Completed source: {0}'.format(source['url']))

    print('- Results written to data.json')

if __name__ == '__main__':
    main()
