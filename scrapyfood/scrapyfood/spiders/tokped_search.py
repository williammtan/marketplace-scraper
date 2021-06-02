import scrapy
import json
from ..gql import TokpedGQL, BaseSpiderGQL
from ..constants import tokped_search_params

MAX_QUERIES = 60 * 100
QUERY_SIZE = 200


class TokpedSearchScraper(BaseSpiderGQL, scrapy.Spider):
    name = 'tokped_search'

    def __init__(self, query_file):
        if type(query_file) == str:
            f = open(query_file)
            self.query_list = json.load(f)
        elif type(query_file) == dict:
            self.query_list = [query_file]
        elif type(query_file) == list:
            self.query_list = query_file

    def start_requests(self):
        for i, query in enumerate(self.query_list):
            for i in range(0, MAX_QUERIES, QUERY_SIZE):
                params = tokped_search_params.format(
                    category=query['category'], start=i)
                yield self.gql.request_old(callback=self.parse_split, params=params)

    def parse(self, response):
        for prod in response['ace_search_product_v4']['data']['products']:
            yield prod

    gql = TokpedGQL(operation_name='SearchProductQueryV4', query="""
    query SearchProductQueryV4($params: String!) {
        ace_search_product_v4(params: $params) {
            data {
                products {
                    id
                    name
                    badges {
                        title
                        imageUrl
                        show
                        __typename
                    }
                    category: departmentId
                    categoryBreadcrumb
                    categoryId
                    categoryName
                    countReview
                    discountPercentage
                    gaKey
                    imageUrl
                    labelGroups {
                        position
                        title
                        type
                        __typename
                    }
                    originalPrice
                    price
                    priceRange
                    rating
                    ratingAverage
                    shop {
                        id
                        name
                        url
                        city
                        isOfficial
                        isPowerBadge
                    }
                    url
                }
            }
        }
    }
    """)
