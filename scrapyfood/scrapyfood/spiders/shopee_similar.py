#######################################################
# Scrape shopee similar products
#######################################################

import scrapy
import pandas as pd
from ..constants import shopee_similar_api, shopee_prod_url, shopee_image_url
from ..items import ShopeeShortProductItem

SIM_LIMIT = 100


class ShopeeSimilarScraper(scrapy.Spider):

    def __init__(self, product_list, scrape_images=False, sections=['from_same_shop', 'you_may_also_like', 'similar_product']):
        self.df = pd.read_csv(product_list)
        self.scrape_images = scrape_images
        self.sections = sections

    def start_requests(self):
        for prod in self.df.iterrows():
            url = shopee_similar_api.format(
                id=prod.id, limit=SIM_LIMIT, shop_id=prod.shop_id)
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        body = response.json()['data']
        sections = [sect for sect in body['sections']
                    if sect['key'] in self.sections]
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
                # 'category': self.category,
                'price': price,
                'image_urls': image_urls,
                'stock': stock,
                'sold': sold,
                'liked_count': liked_count,
                'brand': brand
            })

            prod_item = ShopeeShortProductItem()
            yield prod_item
