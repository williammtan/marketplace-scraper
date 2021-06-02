#######################################################
# Scrape individual products from a list of ids
# Add additional option to list similar products
#######################################################

import scrapy
import pandas as pd
from ..items import ShopeeProductItem
from ..constants import shopee_prod_api, shopee_prod_url, shopee_image_url
from ..utils import read_df


class ShopeeProductScraper(scrapy.Spider):
    name = 'shopee_products'

    def __init__(self, product_list, scrape_images=False):
        self.df = read_df(product_list)
        self.scrape_images = scrape_images

    def start_requests(self):
        is_images = 'images' in self.df.columns
        for i, prod in self.df.iterrows():
            url = shopee_prod_api.format(id=prod.id, shop_id=prod.shop_id)
            images = prod.images if is_images else []
            yield scrapy.Request(url, callback=self.parse, cb_kwargs={'images': images})

    def parse(self, response, images):
        body = response.json()
        if body['error'] is not None:  # last line
            return

        prod = body['item']

        id = prod['itemid']
        shop_id = prod['shopid']
        name = prod['name']
        url = shopee_prod_url.format(name=name, shop_id=shop_id, id=id)
        description = prod['description']
        categories = [{'id': cat['catid'], 'name': cat['display_name']}
                      for cat in prod['categories']]

        price = prod['price'] / 100000000
        stock = prod['stock']
        sold = prod['sold']
        liked_count = prod['liked_count']
        brand = prod['brand']

        image_ids = prod['images']
        image_urls = [shopee_image_url.format(
            id=img_id) for img_id in image_ids] if self.scrape_images else []

        prod_item = ShopeeProductItem({
            'id': id,
            'shop_id': shop_id,
            'name': name,
            'url': url,
            'description': description,
            'categories': categories,
            'price': price,
            'image_urls': image_urls,
            'stock': stock,
            'sold': sold,
            'liked_count': liked_count,
            'brand': brand,
            'images': images
        })
        yield prod_item
