import scrapy
import pandas as pd
import hashlib
from ..constants import shopee_prod_api, shopee_image_url
from ..items import ShopeeImageItem


class ShopeeImageScraper(scrapy.Spider):
    name = 'shopee_images'

    def __init__(self, products_df):
        self.products_df = pd.read_json(products_df)

    def start_requests(self):
        for i, prod in self.products_df.iterrows():
            url = shopee_prod_api.format(id=prod.id, shop_id=prod.shop_id)
            headers = {'referer': prod.url}
            yield scrapy.Request(url=url, headers=headers, callback=self.parse, cb_kwargs={'prod_act': prod})

    def parse(self, response, prod_act):
        prod = response.json()['item']
        id = prod['itemid']
        shop_id = prod['shopid']
        image_ids = prod['images']
        image_urls = [shopee_image_url.format(id=id) for id in image_ids]
        image_paths = [hashlib.sha1(id.encode('utf-8')).hexdigest()
                       for id in image_urls]
        yield ShopeeImageItem({
            'id': id,
            'shop_id': shop_id,
            'image_ids': image_ids,
            'image_paths': image_paths
        })
