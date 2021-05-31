# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapyfoodItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class ImageItem(scrapy.Item):
    image_names = scrapy.Field()
    image_outlets = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()


class PageItem(scrapy.Item):
    products = scrapy.Field()


class ProductItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    title = scrapy.Field()
    price = scrapy.Field()
    description = scrapy.Field()
    weight = scrapy.Field()
    menu = scrapy.Field()
    outlet = scrapy.Field()
    url = scrapy.Field()

    main_category = scrapy.Field()
    sub_category = scrapy.Field()

    image_urls = scrapy.Field()
    images = scrapy.Field()


class PageProductItem(scrapy.Item):
    id = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    main_category = scrapy.Field()
    sub_category = scrapy.Field()
    price = scrapy.Field()

    image_urls = scrapy.Field()
    images = scrapy.Field()


class ShopeeShortProductItem(scrapy.Item):
    id = scrapy.Field()
    shop_id = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
    category = scrapy.Field()
    price = scrapy.Field()

    stock = scrapy.Field()
    sold = scrapy.Field()
    liked_count = scrapy.Field()
    brand = scrapy.Field()

    image_urls = scrapy.Field()
    images = scrapy.Field()


class ShopeeProductItem(scrapy.Item):
    id = scrapy.Field()
    shop_id = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
    description = scrapy.Field()
    categories = scrapy.Field()
    price = scrapy.Field()

    stock = scrapy.Field()
    sold = scrapy.Field()
    liked_count = scrapy.Field()
    brand = scrapy.Field()

    image_urls = scrapy.Field()
    images = scrapy.Field()


class ShopeeImageItem(scrapy.Item):
    id = scrapy.Field()
    shop_id = scrapy.Field()
    image_ids = scrapy.Field()
    image_paths = scrapy.Field()
