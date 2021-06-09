#######################################################
# Scrape shopee similar products
#######################################################

import scrapy
import pandas as pd
from ..constants import shopee_similar_api, shopee_prod_url, shopee_image_url
from ..items import ShopeeShortProductItem
from ..utils import read_df

# SIM_LIMIT = 100


class ShopeeSimilarScraper(scrapy.Spider):
    name = 'shopee_similar'

    def __init__(self, product_list, query_count=50, scrape_images=True, sections=['from_same_shop', 'similar_product']):
        self.df = read_df(product_list)
        self.df = self.df.iloc[::-1]
        self.df = self.df.sample(100)
        self.scrape_images = scrape_images
        self.sections = sections
        self.query_count = query_count

    def start_requests(self):
        for i, prod in self.df.iterrows():
            url = shopee_similar_api.format(
                id=prod.id, limit=self.query_count, shop_id=prod.shop_id, category_id=prod.category)
            yield scrapy.Request(url, callback=self.parse, cb_kwargs={'category': prod.category})

    def parse(self, response, category):
        body = response.json()['data']
        sections = [sect for sect in body['sections']
                    if sect['key'] in self.sections and sect['index'] is not None]
        items = [item for sect in sections for item in sect['data']['item']]

        for prod in items:
            id = prod['itemid']
            shop_id = prod['shopid']
            name = prod['name']
            url = shopee_prod_url.format(name=name, shop_id=shop_id, id=id)

            price = prod['price'] / 100000
            stock = prod['stock']
            sold = prod['sold']
            liked_count = prod['liked_count']
            brand = prod['brand']

            image_ids = prod['images']
            image_urls = [shopee_image_url.format(
                id=img_id) for img_id in image_ids] if self.scrape_images else None

            prod_item = ShopeeShortProductItem({
                'id': id,
                'shop_id': shop_id,
                'name': name,
                'url': url,
                'category': category,
                'price': price,
                'image_urls': image_urls,
                'stock': stock,
                'sold': sold,
                'liked_count': liked_count,
                'brand': brand
            })

            yield prod_item
