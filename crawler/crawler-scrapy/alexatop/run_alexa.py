import subprocess

from scrapy.utils.project import get_project_settings

import alexatop.util as util
from alexatop.spiders.alexa_spider import AlexaSpider

ALEXA_MAX = int(1e6)
CRAWL_NUM = int(100e3)

# Grab Alexa top 1M
sites = util.grab_alexa(ALEXA_MAX)

for start in range(0, ALEXA_MAX, CRAWL_NUM):
    # Get start URLs for current run
    start_urls = ','.join(sites[start:start+CRAWL_NUM])

    # Start the spider and block until completed
    crawl_args = 'urls={0}'.format(start_urls)
    subprocess.call(['scrapy', 'crawl', '-a', crawl_args, 'alexa'])
