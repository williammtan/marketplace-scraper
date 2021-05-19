#######################################################
# Scrape shopee product search
#######################################################

import scrapy
from ..items import ShopeeShortProductItem
from ..constants import shopee_search_api, shopee_prod_url, shopee_image_url

ITEM_LIMIT = 100


class ShopeePageScraper(scrapy.Spider):
    name = 'shopee_page'

    def __init__(self, category='157', brand=None, searchby='pop', order='desc', scrape_images=True):
        self.category = category
        self.brand = brand
        self.order = order
        self.search_by = searchby
        self.scrape_images = scrape_images

    def start_requests(self):
        newest = 0
        for i in range(100):
            newest += ITEM_LIMIT  # max item count
            url = shopee_search_api.format(
                newest=newest, order='desc', search_by=self.search_by, match_id=self.category)
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        body = response.json()
        if body['error'] is not None:  # last line
            return

        products = body['items']
        for prod in products:
            prod_basic = prod['item_basic']
            id = prod['itemid']
            shop_id = prod['shopid']
            name = prod_basic['name']
            url = shopee_prod_url.format(name=name, shop_id=shop_id, id=id)

            price = prod_basic['price'] / 100000
            stock = prod_basic['stock']
            sold = prod_basic['sold']
            liked_count = prod_basic['liked_count']
            brand = prod_basic['brand']

            image_ids = prod_basic['images']
            image_urls = [shopee_image_url.format(
                id=img_id) for img_id in image_ids] if self.scrape_images else None

            prod_item = ShopeeShortProductItem({
                'id': id,
                'shop_id': shop_id,
                'name': name,
                'url': url,
                'category': self.category,
                'price': price,
                'image_urls': image_urls,
                'stock': stock,
                'sold': sold,
                'liked_count': liked_count,
                'brand': brand
            })

            yield prod_item
