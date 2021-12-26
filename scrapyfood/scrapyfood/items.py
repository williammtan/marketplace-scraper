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
    strike_price = scrapy.Field()
    discount = scrapy.Field()

    description = scrapy.Field()
    weight = scrapy.Field()
    menu_id = scrapy.Field()
    menu_name = scrapy.Field()
    min_order = scrapy.Field()
    max_order = scrapy.Field()
    condition = scrapy.Field()
    stock = scrapy.Field()
    url = scrapy.Field()

    wholesale_quantity = scrapy.Field()
    wholesale_price = scrapy.Field()

    # shop_name = scrapy.Field()
    # shop_alias = scrapy.Field()
    shop_id = scrapy.Field()

    main_category = scrapy.Field()
    sub_category = scrapy.Field()

    view_count = scrapy.Field()
    review_count = scrapy.Field()
    talk_count = scrapy.Field()
    rating = scrapy.Field()
    sold = scrapy.Field()
    transactions = scrapy.Field()

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

class TokpedShopSpeedItem(scrapy.Item):
    id = scrapy.Field()
    response_speed = scrapy.Field()

class TokpedShopItem(scrapy.Item):
    """Output of tokped_shops process"""
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

    satisfaction = scrapy.Field()
    rating = scrapy.Field()
    reputation = scrapy.Field()

    response_speed = scrapy.Field()

class TokpedCategoryItem(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    identifier = scrapy.Field()
    parent = scrapy.Field() # id for parent, 0 if it doesnt exist
    level = scrapy.Field() # 1, 2, 3
    url = scrapy.Field()
    is_food = scrapy.Field() # if the category's level parent is not /makanan-minuman/

class TokpedCategoryGrowthItem(scrapy.Item):
    id = scrapy.Field()
    product_count = scrapy.Field()

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
