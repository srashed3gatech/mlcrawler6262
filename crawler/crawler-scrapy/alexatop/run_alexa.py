from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor

import alexatop.util as util
from alexatop.spiders.alexa_spider import AlexaSpider

ALEXA_MAX = int(1e6)
CRAWL_NUM = int(100e3)

# Grab Alexa top 1M
sites = util.grab_alexa(ALEXA_MAX)
stop = False

for start in range(0, ALEXA_MAX, CRAWL_NUM):
    # Generate new log file for run
    settings = get_project_settings()
    runner = CrawlerRunner(settings)

    # Get start URLs for current run
    start_urls = sites[start:start+CRAWL_NUM]

    # Start the spider and block until completed
    d = runner.crawl(AlexaSpider, urls=start_urls)
    d.addBoth(lambda _: reactor.stop())

    reactor.run()
