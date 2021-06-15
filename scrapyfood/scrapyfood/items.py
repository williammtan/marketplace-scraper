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
    menu_id = scrapy.Field()
    menu_name = scrapy.Field()
    min_order = scrapy.Field()
    max_order = scrapy.Field()
    condition = scrapy.Field()
    stock = scrapy.Field()
    url = scrapy.Field()

    shop_name = scrapy.Field()
    shop_alias = scrapy.Field()
    shop_id = scrapy.Field()

    main_category = scrapy.Field()
    sub_category = scrapy.Field()

    view_count = scrapy.Field()
    review_count = scrapy.Field()
    talk_count = scrapy.Field()
    rating = scrapy.Field()
    sold = scrapy.Field()

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
    shop_domain = scrapy.Field()
    image_urls = scrapy.Field()

    rating = scrapy.Field()
    review_count = scrapy.Field()
    sold = scrapy.Field()

    ref = scrapy.Field()
    main_category = scrapy.Field()
    sub_category = scrapy.Field()


class TokpedAutocompleteItem(scrapy.Item):
    from_keyword = scrapy.Field()
    keyword = scrapy.Field()


class TokpedShopCoreItem(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    alias = scrapy.Field()
    description = scrapy.Field()
    tagline = scrapy.Field()
    active_products = scrapy.Field()
    location = scrapy.Field()
    is_closed = scrapy.Field()

    products_sold = scrapy.Field()
    transaction_count = scrapy.Field()
    favourite_count = scrapy.Field()

    started_at = scrapy.Field()


class TokpedShopStatisticItem(scrapy.Item):
    id = scrapy.Field()
    satisfaction = scrapy.Field()
    rating = scrapy.Field()
    reputation = scrapy.Field()


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
