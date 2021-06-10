# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import json
import subprocess
from time import process_time
from numpy.random import Generator
import logging
from scrapy import signals
from scrapy.utils.project import get_project_settings
from w3lib.http import basic_auth_header

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
from scrapyfood.constants import proxy_base, proxy_api
from nordvpn_switcher import initialize_VPN, rotate_VPN, terminate_VPN
import time


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
        self.request_count = 0
        logging.info('initialized vpn')
        self.vpn_process = subprocess.Popen(
            ['openpyn', '-s', vpn_servers[0]], stdin=subprocess.PIPE)
        time.sleep(20)

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        def request(r):
            # combine the requests
            body = [json.loads(r.body) for r in self.request_cue]
            json_body = json.dumps(body)
            logging.debug('Sending requests')
            yield r.replace(body=json_body, cb_kwargs={'args': [r.cb_kwargs for r in self.request_cue]})
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
                        self.request_count += 1
                        if self.request_count % 400 == 0 and self.request_count != 0:
                            self.vpn_process.kill()
                            index = int(self.request_count / 400)
                            logging.info(
                                f"Rotating vpn to {vpn_servers[index]}")
                            self.vpn_process = subprocess.Popen(
                                ['openpyn', '-s', vpn_servers[index]], stdin=subprocess.PIPE)
                        yield from request(r)

                except StopIteration:
                    logging.debug('Running end request')
                    yield from request(r)
                    break


class VPNMiddleware:
    def __init__(self):
        self.request_count = 0
        print('initialized vpn')
        initialize_VPN(save=1, area_input=['complete rotation singapore'])

    def process_start_requests(self, start_request, spider):
        for r in start_request:
            self.request_count += 1
            if self.request_count % 400 == 0:
                print('roatating vpn')
                rotate_VPN()
            yield r


class ProxyMiddleware(object):
    def process_request(self, request, spider):
        if not request.url.endswith('&keep_headers=true') and not request.url.startswith('https://images.tokopedia.net'):
            request = request.replace(url=proxy_base.format(url=request.url))
            return request
        # print(request.url)
        # request.meta['proxy'] = proxy_api
        # print(proxy_api)
        # return request
        # print(request)


vpn_servers = ['sg455',
               'sg456',
               'sg457',
               'sg458',
               'sg459',
               'sg460',
               'sg461',
               'sg462',
               'sg463',
               'sg464',
               'sg465',
               'sg466',
               'sg467',
               'sg468',
               'sg469',
               'sg470',
               'sg471',
               'sg472',
               'sg473',
               'sg474',
               'sg475',
               'sg476',
               'sg477',
               'sg478',
               'sg479',
               'sg480',
               'sg481',
               'sg482',
               'sg483',
               'sg484',
               'sg485',
               'sg486',
               'sg487',
               'sg488',
               'sg489',
               'sg490',
               'sg491',
               'sg492',
               'sg493',
               'sg494',
               'sg495',
               'sg496',
               'sg497',
               'sg498',
               'sg499',
               'sg500',
               'sg501',
               'sg502',
               'sg503',
               'sg504',
               'sg505',
               'sg506',
               'sg507',
               'sg508']
