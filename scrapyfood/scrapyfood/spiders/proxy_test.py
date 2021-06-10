import scrapy
import json


class ProxyTestSpider(scrapy.Spider):
    name = 'proxy_test'

    def start_requests(self):
        headers = {'referer': 'aaaa', 'content-type': 'application/json'}
        body = json.dumps(
            {"query": "query Ticker($page: String) {\n  ticker {\n    tickers(page: $page) {\n      message\n      __typename\n }\n    __typename\n  }\n}", "variables": {"page": "header"}})

        yield scrapy.Request(url='https://httpbin.org/ip', headers=headers, body=body)
        yield scrapy.Request(url='https://httpbin.org/ip', headers=headers, body=body)
        yield scrapy.Request(url='https://gql.tokopedia.com', method='POST', headers=headers, body=body)

    def parse(self, response):
        print(response.text)
        print(response.status)
        print(response.request.headers)
        assert response.status == 200
        body = response.json()
        # assert 'error' not in body.keys()
        # assert 'data' in body.keys()
        # assert body['data'] is not None
