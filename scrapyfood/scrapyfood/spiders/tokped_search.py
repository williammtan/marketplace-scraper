import scrapy
import jsonlines
import json
from ..gql import TokpedGQL, BaseSpiderGQL
from ..items import TokpedShortProduct, TokpedAutocompleteItem
from ..constants import tokped_search_params
from ..utils import read_terjual_tokped, create_tokped_params, read_rp_tokped
import itertools
import logging
import re
from scrapy.utils.project import get_project_settings
from scrapy import signals
from pydispatch import dispatcher

QUERY_SIZE = 200
settings = get_project_settings()
if 'TEST' in settings.keys() and settings['TEST']:
    MAX_QUERIES = 200
else:
    MAX_QUERIES = 60 * 100


class TokpedSearchScraper(BaseSpiderGQL, scrapy.Spider):
    name = 'tokped_search'

    def __init__(self, query_file, related_output=None, max_queries=6000):
        self.max_queries = max_queries or MAX_QUERIES
        if type(query_file) == str:
            f = open(query_file)
            self.query_list = json.load(f)
        elif type(query_file) == list:
            self.query_list = query_file

        self.related_output = related_output
        self.related_keywords = []
        dispatcher.connect(self.quit, signals.spider_closed)

    def start_requests(self):
        settings = [
            param for param in self.query_list if param['type'] == 'setting']
        parameters = [
            param for param in self.query_list if param['type'] == 'parameter']

        param_combinations = list(itertools.product(
            *[[value for value in param['values']] for param in parameters]))

        param_configs = [{p['id']: comb[i] for i, p in enumerate(
            parameters)} for comb in param_combinations]
        setting_configs = {sett['id']: {
            'name': sett['name'], 'value': sett['value']} for sett in settings}

        for param in param_configs:
            setting_configs.update(param)
            param_string = create_tokped_params(setting_configs)
            yield from self.scrape_config(param_string)

    def scrape_config(self, config):
        logging.info(f'Scraping config: {config}')
        for i in range(0, self.max_queries, QUERY_SIZE):
            query = config + f'&start={i}'
            yield self.gql.request_old(callback=self.parse_split, params=query, cb_kwargs={'ref_params': query})

    def parse(self, response, ref_params):
        data = response['ace_search_product_v4']['data']
        related_keywords = data['related']['otherRelated']
        [self.related_keywords.append(k['keyword']) for k in related_keywords]

        for prod in data['products']:
            old_price = read_rp_tokped(prod['originalPrice'])
            discounted_price = read_rp_tokped(prod['price'])
            sold = read_terjual_tokped(prod['labelGroups'])

            category_breadcrumb = prod['categoryBreadcrumb']
            sub_category = category_breadcrumb.split('/')[-1]
            sub_category_lower = '-'.join([split for split in re.split(
                r" |\-|&", sub_category.lower()) if split != ''])

            yield TokpedShortProduct({
                'id': prod['id'],
                'name': prod['name'],
                'category_breadcrumb': category_breadcrumb,
                'prod_url': prod['url'],
                'old_price': old_price,
                'discounted_price': discounted_price,
                'discount_percent': prod['discount'],
                'stock': prod['stock'],
                'shop': prod['shop']['id'],
                'image_urls': [prod['image_urls']],

                'review_count': prod['review_count'],
                'rating': prod['ratingAverage'],
                'sold': sold,

                'ref': ref_params,
                'sub_category': sub_category_lower
            })

    def quit(self):
        if self.related_output is not None:
            with jsonlines.open(self.related_output, mode='a') as writer:
                for k in self.related_keywords:
                    writer.write(k)

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
                    review_count: countReview
                    discount: discountPercentage
                    gaKey
                    image_urls: imageUrl
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
                    stock
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
                related {
                    otherRelated {
                        keyword
                    }
                }
            }
        }
    }
    """)


class TokpedAutocompleteScraper(scrapy.Spider, BaseSpiderGQL):
    name = 'tokped_autocomplete'

    def __init__(self, keywords, max_depth=2):
        """Get autocomplete suggestions from keywords"""
        if type(keywords) == str:
            self.keywords = json.loads(keywords)
        else:
            self.keywords = keywords
        self.max_depth = max_depth
        self.depth = 0

    def make_param(self, keyword):
        return tokped_search_params + f'&q={keyword}'

    def start_requests(self):
        for k in self.keywords:
            param = self.make_param(k)
            yield self.gql.request_old(callback=self.parse_split, cb_kwargs={
                'from_keyword': k}, param=param)

    def parse(self, response, from_keyword):
        data = response['universe_suggestion']['data']
        keyword_suggestions = [
            k['title'] for k in data['items'] if k['type'] == 'keyword']
        for k in keyword_suggestions:
            yield TokpedAutocompleteItem({
                'from_keyword': from_keyword,
                'keyword': k
            })
            if self.depth <= self.max_depth:
                param = self.make_param(k)
                yield self.gql.request_old(callback=self.parse_split, cb_kwargs={
                    'from_keyword': k}, param=param)

    gql = TokpedGQL(operation_name="AutocompleteQuery", query="""query AutocompleteQuery($param: String) {
  universe_suggestion(param: $param) {
    data {
      id
      name
      items {
        discountPercentage: discount_percentage
        originalPrice: original_price
        template
        type
        applink
        url
        title
        subtitle
        icon_title
        icon_subtitle
        shortcut_image
        image_url
        url_tracker
        tracking {
          code
          __typename
        }
        __typename
      }
      __typename
    }
    __typename
  }
}
""")
