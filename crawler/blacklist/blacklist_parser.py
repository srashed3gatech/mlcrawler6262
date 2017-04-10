import re
import os
import sys
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
BLACKLIST_SOURCES = {
    'psh': {'url': 'https://hosts-file.net/psh.txt', 'format': 'hosts', 'type': 'phish'},
    'exp': {'url': 'https://hosts-file.net/exp.txt', 'format': 'hosts', 'type': 'exploit'},
    'emd': {'url': 'https://hosts-file.net/emd.txt', 'format': 'hosts', 'type': 'malware'},
    'fsa': {'url': 'https://hosts-file.net/fsa.txt', 'format': 'hosts', 'type': 'fraud'},
    'domains': {'url': 'http://mirror2.malwaredomains.com/files/domains.txt', 'format': 'malwaredomains', 'type': 'all'},
    'suspicious': {'url': 'https://isc.sans.edu/feeds/suspiciousdomains_Medium.txt', 'format': 'url', 'type': 'all'},
}

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

def dump_results(parser, source):
    '''Given a parser, extract results, and write to globally defined output file.'''
    # Dump results into TXT file (append)
    with open(OUTPUT_FILE, 'a') as f:
        for result in parser.results:
            f.write('{0},{1}\n'.format(result['url'], result['type']))

    print('- Completed source: {0}'.format(source))

def main():
    # Remove today's file if it exists
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    # Take local files in place of remote blacklist URLs
    if len(sys.argv) > 1:
        files = sys.argv[1:]

        print('Starting local blacklist parser..')
        print('Blacklist files: ' + ', '.join(files))

        sources = BLACKLIST_SOURCES.keys()

        for each in files:
            # Read file lines for parsing
            with open(each, 'r') as f:
                lines = f.readlines()

            # Find correct blacklist source for given file based on name
            for s in sources:
                if s in each:
                    source = BLACKLIST_SOURCES[s]

            parser = BlacklistParser(lines, source['format'], 'n/a')
            dump_results(parser=parser, source=each)

    # Otherwise, get remote blacklists
    else:
        print('Starting remote blacklist parser...')

        # Grab each of the blacklists and parse them
        for source in BLACKLIST_SOURCES.values():
            r = urllib.request.urlopen(source['url'])
            lines = r.read().decode('utf-8').split('\n')

            b = BlacklistParser(lines, source['format'], source['type'])
            dump_results(parser=b, source=source['url'])

    print('Done! All results written to {0}.'.format(OUTPUT_FILE))

if __name__ == '__main__':
    main()
