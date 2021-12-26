import re
import json
import pandas as pd
import numpy as np
import scrapy
from ..gql import TokpedGQL, BaseSpiderGQL
from ..utils import read_df, df_to
from ..items import TokpedCategoryItem, TokpedCategoryGrowthItem
from pydispatch import dispatcher

class TokpedCategoryScraper(BaseSpiderGQL, scrapy.Spider):
    name = 'tokped_category'

    def start_requests(self):
        yield self.gql.request_old(callback=self.parse_split)

    def parse(self, response):
        for main_category in response['CategoryAllList']['categories']:
            if main_category['id'] == "0":
                continue # skip "Pilihan Untukmu"
            is_food = main_category['id'] == "35"
            yield TokpedCategoryItem({
                'id': int(main_category['id']),
                'name': main_category['name'],
                'identifier': main_category['identifier'],
                'parent': 0, # no parent
                'level': 1,
                'url': f'https://www.tokopedia.com/p/{main_category["identifier"]}',
                'is_food': is_food
            })
            for sub_category in main_category['child']:
                yield TokpedCategoryItem({
                    'id': int(sub_category['id']),
                    'name': sub_category['name'],
                    'identifier': sub_category['url'].split('/')[-1],
                    'parent': int(main_category['id']), # no parent
                    'level': 2,
                    'url': sub_category['url'],
                    'is_food': is_food
                })
                for sub_sub_category in sub_category['child']:
                    yield TokpedCategoryItem({
                        'id': int(sub_sub_category['id']),
                        'name': sub_sub_category['name'],
                        'identifier': sub_sub_category['url'].split('/')[-1],
                        'parent': int(sub_category['id']), # no parent
                        'level': 3,
                        'url': sub_sub_category['url'],
                        'is_food': is_food
                    })

    gql = TokpedGQL(operation_name='categoryAllList', query="""
    query categoryAllList($categoryID: Int, $type: String) {
  CategoryAllList: categoryAllList(categoryID: $categoryID, type: $type) {
    categories {
      identifier
      name
      id
      child {
        id
        template
        name
        url
        iconImageUrl
        child {
          name
          url
          id
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

class TokpedCategoryGrowthScraper(scrapy.Spider):
    name = 'tokped_category_growth'

    def __init__(self, categories):
        if type(categories) == str:
            self.categories = read_df(categories)
        else:
            self.categories = categories

        self.categories['product_count'] = np.nan
        self.categories = self.categories.set_index('id')

    def start_requests(self):
        # scrape all categories that are not main category
        for id, category in self.categories[self.categories['level'] != 1].iterrows():
            yield scrapy.Request(category['url'], cb_kwargs={'id': id})

    def parse(self, response, id):
        div = response.css('.css-1dq1dix').get()
        product_count = int(re.findall("Menampilkan<!-- --> <!-- -->(\d+)", div)[0])
        self.categories.loc[id, 'product_count'] = product_count
        yield TokpedCategoryGrowthItem({
            'id': id,
            'product_count': product_count
        })

        if self.categories.loc[id, 'level'] == 2: # if sub category
            yield from self.calculate_main_category(self.categories.loc[id, 'parent'])
    
    def calculate_main_category(self, id):
        child = self.categories[self.categories['parent']==id]
        if not np.any(child.product_count.isnull()):
            product_count = child.product_count.sum()
            yield TokpedCategoryGrowthItem({
                'id': int(id),
                'product_count': int(product_count)
            })

