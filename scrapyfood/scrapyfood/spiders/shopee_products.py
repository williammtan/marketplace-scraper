#######################################################
# Scrape individual products from a list of ids
# Add additional option to list similar products
#######################################################

import scrapy
import pandas as pd
from ..items import ShopeeProductItem
from ..constants import shopee_prod_api, shopee_prod_url, shopee_image_url


class ShopeeProductScaper(scrapy.Spider):
    base_api = 'https://shopee.co.id/api/v2/item/get?itemid={id}&shopid={shop_id}'
    base_prod_url = 'https://shopee.co.id/{name}-i.{shop_id}.{id}'

    def __init__(self, product_list, scrape_images=False):
        self.df = pd.read_csv(product_list)
        self.scrape_images = scrape_images

    def start_requests(self):
        for prod in self.df.iterrows():
            url = shopee_prod_api.format(id=prod.id, shop_id=prod.shop_id)
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        body = response.json()
        if body['error'] is not None:  # last line
            return

        prod = body['item']

        id = prod['itemid']
        shop_id = prod['shopid']
        name = prod['name']
        url = shopee_prod_url.format(name=name, shop_id=shop_id, id=id)
        description = prod['description']

        price = prod['price'] / 100000000
        stock = prod['stock']
        sold = prod['sold']
        liked_count = prod['liked_count']
        brand = prod['brand']

        image_ids = prod['images']
        image_urls = [shopee_image_url.format(
            img_id) for img_id in image_ids] if self.scrape_images else None

        prod_item = ShopeeProductItem({
            'id': id,
            'shop_id': shop_id,
            'name': name,
            'url': url,
            'description': description,
            'category': self.category,
            'price': price,
            'image_urls': image_urls,
            'stock': stock,
            'sold': sold,
            'liked_count': liked_count,
            'brand': brand
        })
        yield prod_item
