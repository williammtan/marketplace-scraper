# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from pandas.core.groupby.generic import ScalarResult
import scrapy


class ImageItem(scrapy.Item):
    image_names = scrapy.Field()
    image_outlets = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()


class TokpedProduct(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    alias = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    description = scrapy.Field()
    weight = scrapy.Field()
    menu = scrapy.Field()
    shop_name = scrapy.Field()
    shop_id = scrapy.Field()
    stock = scrapy.Field()
    url = scrapy.Field()

    main_category = scrapy.Field()
    sub_category = scrapy.Field()

    view_count = scrapy.Field()
    review_count = scrapy.Field()
    talk_count = scrapy.Field()
    rating = scrapy.Field()

    image_urls = scrapy.Field()
    images = scrapy.Field()


class TokpedPageProduct(scrapy.Item):
    id = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    main_category = scrapy.Field()
    sub_category = scrapy.Field()
    price = scrapy.Field()

    image_urls = scrapy.Field()
    images = scrapy.Field()


class TokpedShortProduct(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    category_breadcrumb = scrapy.Field()
    prod_url = scrapy.Field()
    old_price = scrapy.Field()
    discounted_price = scrapy.Field()
    discount_percent = scrapy.Field()
    stock = scrapy.Field()
    shop = scrapy.Field()
    image_urls = scrapy.Field()

    rating = scrapy.Field()
    review_count = scrapy.Field()
    sold = scrapy.Field()

    ref = scrapy.Field()
    sub_category = scrapy.Field()


class TokpedAutocompleteItem(scrapy.Item):
    from_keyword = scrapy.Field()
    keyword = scrapy.Field()


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

    ref = scrapy.Field()


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
