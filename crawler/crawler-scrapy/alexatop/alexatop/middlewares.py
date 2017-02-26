# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

import logging
import random

logger = logging.getLogger(__name__)

class AlexaDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    def __init__(self, user_agents):
        self.user_agents = user_agents

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(settings['USER_AGENTS'])
    
    def process_request(self, request, spider):
        request.headers['User-Agent'] = random.choice(self.user_agents)
        yield request
