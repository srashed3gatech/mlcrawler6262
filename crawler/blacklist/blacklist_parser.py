import re
import os
import urllib.request
from datetime import datetime

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

# TODO: Add OpenPhish as source
BLACKLIST_SOURCES = [
    {'url': 'https://hosts-file.net/psh.txt', 'format': 'hosts', 'type': 'phish'},
    {'url': 'https://hosts-file.net/exp.txt', 'format': 'hosts', 'type': 'exploit'},
    {'url': 'https://hosts-file.net/emd.txt', 'format': 'hosts', 'type': 'malware'},
    {'url': 'https://hosts-file.net/fsa.txt', 'format': 'hosts', 'type': 'fraud'},
    {'url': 'http://mirror2.malwaredomains.com/files/domains.txt', 'format': 'malwaredomains', 'type': 'all'},
    {'url': 'https://isc.sans.edu/feeds/suspiciousdomains_Medium.txt', 'format': 'url', 'type': 'all'},
]

DATE_FORMAT = '%Y-%m-%d'

def format_date(dt, fmt=DATE_FORMAT):
    return datetime.strftime(dt, fmt)

TODAY = format_date(datetime.now())

OUTPUT_FILE = 'blacklist-{0}.csv'.format(TODAY)

class BlacklistParser:
    '''
        Parses a blacklist of a given format.

        Throws: Exception
    '''
    def __init__(self, lines, f, t):
        self.results = []
        self.format = f
        self.type = t

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
            result['type'] = self.type
        elif self.format == 'malwaredomains':
            result['url'] = groups[0].strip()
            result['type'] = groups[1].strip()
        elif self.format == 'url':
            result['url'] = groups.strip()
            result['type'] = self.type

        return result

def main():
    # Remove existing data.json
    try:
        os.remove(OUTPUT_FILE)
    except OSError:
        pass

    # Grab each of the blacklists and parse them
    for source in BLACKLIST_SOURCES:
        r = urllib.request.urlopen(source['url'])
        lines = r.read().decode('utf-8').split('\n')

        b = BlacklistParser(lines, source['format'], source['type'])

        # Dump results into TXT file (append)
        with open(OUTPUT_FILE, 'a') as f:
            for result in b.results:
                f.write('{0},{1}\n'.format(result['url'], result['type']))

        print('- Completed source: {0}'.format(source['url']))

    print('- Results written to {0}'.format(OUTPUT_FILE))

if __name__ == '__main__':
    main()
