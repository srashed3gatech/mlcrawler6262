import os
import subprocess

from scrapy.utils.project import get_project_settings

import alexatop.util as util
from alexatop.spiders.alexa_spider import AlexaSpider

ALEXA_MAX = int(1e6)
START_RANK = 1
CRAWL_NUM = int(100e3)

URLS_DIR = os.path.join(os.getcwd(), 'urls')
os.makedirs(URLS_DIR, exist_ok=True) # Create the folder

# Grab Alexa top 1M
sites = util.grab_alexa(ALEXA_MAX)

for start in range(START_RANK-1, ALEXA_MAX, CRAWL_NUM):
    # Get start URLs for current run
    start_urls = '\n'.join(sites[start:start+CRAWL_NUM])

    # Write URLs of current run to a unique file
    url_file = os.path.join(URLS_DIR, '{0}-{1}'.format(start+1, start+CRAWL_NUM))
    with open(url_file, 'w') as f:
        f.write(start_urls)

    # Start the spider and block until completed
    # Pass path to current file
    crawl_args = 'urls_file={0}'.format(url_file)
    subprocess.call(['scrapy', 'crawl', '-a', crawl_args, 'alexa'])

    # Delete the URLs file
    os.remove(url_file)
