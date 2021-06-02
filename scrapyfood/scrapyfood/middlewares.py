# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import json
from numpy.random import Generator
import scrapy
from scrapy import signals
from scrapy.utils.project import get_project_settings
from w3lib.http import basic_auth_header

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
from scrapyfood.constants import proxy_url


class ScrapyfoodSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ScrapyfoodDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class TokpedGQLSpiderMiddleware:
    request_cue = []

    def __init__(self):
        self.cue_size = get_project_settings()['REQUEST_CUE']

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        def request(r):
            # combine the requests
            body = [json.loads(r.body) for r in self.request_cue]
            json_body = json.dumps(body)
            yield r.replace(body=json_body, cb_kwargs={'kwargs': [r.cb_kwargs for r in self.request_cue]})
            self.request_cue = []

        if type(start_requests) == tuple:
            # Must return only requests (not items).
            for i, r in enumerate(start_requests):
                self.request_cue.append(r)
                if len(self.request_cue) == self.cue_size:
                    # TODO: assert that the requests have the same body
                    yield from request(r)
                elif i == len(start_requests):
                    # end of tuple
                    yield from request(r)
        else:
            while True:
                try:
                    r = next(start_requests)
                    self.request_cue.append(r)
                    if len(self.request_cue) == self.cue_size:
                        # TODO: assert that the requests have the same body
                        print('Sending requests')
                        yield from request(r)

                except StopIteration:
                    request(r)
                    break


class ProxyMiddleware(object):
    def process_request(self, request, spider):
        request.meta['proxy'] = proxy_url
