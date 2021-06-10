import scrapy
from w3lib.html import remove_tags
from ..utils import get_cache
from ..items import TokpedProduct
from ..categories import main_categories, sub_categories
import re


class TokpedPageSpider(scrapy.Spider):
    name = "tokped_pages"
    max_depth = 2
    # allowed_domains = 'https://tokopedia.com/'

    def __init__(self, category_url='makanan-ringan/camilan-instant'):
        base_url = 'https://www.tokopedia.com/p/makanan-minuman' + category_url
        base_url = base_url + '?page={page}'
        self.start_urls = [base_url.format(page=i) for i in range(1, 101)]
        self.main_category = category_url.split('/')[-2]
        self.sub_category = category_url.split('/')[-1]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse,
                                 # meta={"proxy": "http://scraperapi:5b7afb62c67de1477c5359799c6d3607@proxy-server.scraperapi.com:8001"}
                                 )

    def parse(self, response):
        cache_data = get_cache(response)

        r_query = re.compile(r"^\$ROOT_QUERY\.searchProduct")
        query_key = list(filter(r_query.match, cache_data.keys()))[0]

        # get list of products
        products = cache_data[query_key]["products"]
        product_ids = [product["id"]
                       for product in products]  # get product ids

        for id in product_ids:

            search_url = 'https://www.tokopedia.com/search?st=product&q={query}'
            yield scrapy.Request(search_url.format(query=cache_data[id]["name"]), callback=self.parse_search)

            # yield scrapy.Request(product_url, self.parse_product, cb_kwargs={'depth': depth})\

    def parse_search(self, response):
        cache_data = get_cache(response)

        r_query = re.compile(r"^\$ROOT_QUERY\.ace_search_product_v4.*\.data$")
        match = re.search(r_query, '$ROOT_QUERY.ace_search_product_v4({\"params\":\"device=desktop&ob=23&page=1&q=Kata%20Oma%20Telur%20Gabus%20Rasa%20Gula%20Aren%20-%2063gr&related=true&rows=60&safe_search=false&scheme=https&shipping=&source=search&st=product&start=0&topads_bucket=true&unique_id=915e221fb1dd692b37cbb7233d98f421&user_addressId=&user_cityId=&user_districtId=&user_id=&user_lat=&user_long=&user_postCode=&variants=\"}).data')
        query_key = list(filter(r_query.match, cache_data.keys()))[0]

        # get list of products
        products = cache_data[query_key]["products"]
        product_ids = [product["id"]
                       for product in products]  # get product ids
        for id in product_ids:
            product = cache_data[id]
            productItem = TokpedPageProduct({
                'id': product['id'],
                'title': product['name'],
                'url': product['url'],
                'price': product['price'],
                'image_urls': [product['imageUrl']],
                'main_category': self.main_category,
                'sub_category': self.sub_category
            })
            yield productItem

    def parse_product(self, response, depth):
        cache_data = get_cache(response)

        url = "".join(response.url.split("?")[0])
        item_alias = url.split("/")[-1]
        store = url.split("/")[-2]

        base_query_key = (
            '$ROOT_QUERY.pdpGetLayout({"apiVersion":1,"layoutID":"","productKey":"'
            + item_alias
            + '","shopDomain":"'
            + store
            + '","userLocation":{"addressID":"0","districtID":"0","latlon":"","postalCode":""}})'
        )
        base_query = cache_data[base_query_key]
        id = base_query["basicInfo"]["id"]
        item_data = cache_data[id]

        product_item = TokpedProduct()

        # TITLE AND DESCRIPTIONS
        title = response.css("h2.css-1fqpg99-unf-heading::text").get()

        description_raw = response.css(
            "span.css-o0scwi span.css-168ydy0 div").get()
        description_clean = (
            remove_tags(description_raw) if (
                description_raw is not None) else None
        )
        product_item['title'] = title
        product_item['description'] = description_clean
        product_item['outlet'] = store

        # WEIGHT, MENU AND PRICE
        weight = f'{item_data["weight"]} {item_data["weightUnit"]}'

        price_query = cache_data[base_query_key + ".components.3.data.0.price"]
        price = price_query["value"]

        menu_key = item_data["menu"]["id"]
        menu = cache_data[menu_key]["name"]

        product_item['weight'] = weight
        product_item['price'] = price
        product_item['menu'] = menu

        # CATEGORIES
        category_key = item_data["category"]["id"]
        category_data = cache_data[category_key]
        category_names = [
            cache_data[category["id"]]["name"] for category in category_data["detail"]
        ]
        main_cat = [
            cat for cat in category_names if cat in main_categories][0]
        sub_cat = [cat for cat in category_names if cat in sub_categories][0]

        product_item['main_category'] = main_cat
        product_item['sub_category'] = main_cat

        # IMAGES
        media_query = re.compile(r".*\.media\.")
        media_keys = list(filter(media_query.match, cache_data.keys()))
        image_urls = [cache_data[key]["URLThumbnail"] for key in media_keys]

        yield product_item

        # SIMILAR IMAGES BY SEARCH QUERY
        search_url = 'https://www.tokopedia.com/search?st=product&q={query}'
        if depth < self.max_depth:
            yield scrapy.Request(search_url.format(query=title), callback=self.parse, cb_kwargs={'depth': depth + 1})
