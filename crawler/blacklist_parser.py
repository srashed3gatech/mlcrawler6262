import re
from datetime import datetime

import pysolr
import requests

'''
    Formats:
        - hosts: HOSTS file format (127.0.0.1 -> URL)
        - malwaredomains: see regexes
        - url: one URL per line
'''
FORMATS = ['hosts', 'malwaredomains', 'url']

REGEXES = {
    'hosts': re.compile(r'\S+\s+(\S+)'),
    'malwaredomains': re.compile(r'(\S+)\s+(\S+)\s+(\S+)\s+(\S+)'),
    'url': re.compile(r'(\S+)')
}

BLACKLIST_SOURCES = [
    {'url': 'https://hosts-file.net/psh.txt', 'format': 'hosts', 'type': 'phish'},
    {'url': 'https://hosts-file.net/exp.txt', 'format': 'hosts', 'type': 'exploit'},
    {'url': 'https://hosts-file.net/emd.txt', 'format': 'hosts', 'type': 'malware'},
    {'url': 'https://hosts-file.net/psh.txt', 'format': 'hosts', 'type': 'phish'},
    {'url': 'http://mirror2.malwaredomains.com/files/domains.txt', 'format': 'malwaredomains', 'type': 'all'},
    {'url': 'https://isc.sans.edu/feeds/suspiciousdomains_Medium.txt', 'format': 'url', 'type': 'all'},
]

TODAY = datetime.strftime(datetime.now(), '%Y%M%d')

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
            groups = re.findall(p, line)[0]
        except:
            return None

        # Invalid line, skip it
        if len(groups) == 0:
            return None

        result = {}

        # Extract fields from regex output
        if self.format == 'host':
            result['url'] = groups[0].strip()
        elif self.format == 'malwaredomains':
            result['url'] = groups[0].strip()
            result['type'] = groups[1].strip()
            result['source'] = groups[2].strip()
            result['date'] = groups[3].strip()
        elif self.format == 'url':
            result['url'] = groups[0].strip()

        if self.format != 'malwaredomains':
            result['type'] = 'all'
            result['source'] = 'unknown'
            result['date'] = TODAY

        return result

def main():
    urls = []

    # Grab each of the blacklists and parse them
    for source in BLACKLIST_SOURCES:
        r = requests.get(source['url'])
        lines = r.text.split('\n')

        b = BlacklistParser(lines, source['format'])
        urls += b.results

    # Store everything in a Solr collection
    

if __name__ == '__main__':
    main()
