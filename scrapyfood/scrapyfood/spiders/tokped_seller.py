import scrapy
from ..gql import TokpedGQL, BaseSpiderGQL
import json


class TokpedSellerScraper(scrapy.Spider, BaseSpiderGQL):
    name = 'tokped_seller'

    def __init__(self, sellers_ids):
        if type(sellers_ids) == str:
            sellers_ids = json.load(open(sellers_ids))

    def start_requests(self):
        pass

    gql = TokpedGQL(operation_name='')
