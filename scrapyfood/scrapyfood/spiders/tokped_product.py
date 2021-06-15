from os import read
from subprocess import call
import scrapy
from ..utils import read_df, calculate_weight
from ..items import TokpedProduct
from ..gql import BaseSpiderGQL, TokpedGQL


class TokpedProductScraper(BaseSpiderGQL, scrapy.Spider):
    name = 'tokped_products'

    def __init__(self, product_list):
        self.product_list = read_df(product_list)
        if 'prod_url' in self.product_list.columns:
            if 'shop_domain' not in self.product_list.columns:
                self.product_list['shop_domain'] = self.product_list.apply(
                    lambda x: x.prod_url.split('/')[-2], axis=1)
            if 'name_domain' not in self.product_list.columns:
                self.product_list['name_domain'] = self.product_list.apply(
                    lambda x: x.prod_url.split('/')[-1].split('?')[0], axis=1)

    def start_requests(self):
        for i, prod in self.product_list.iterrows():
            yield self.gql.request_old(callback=self.parse_split, headers={'x-tkpd-akamai': 'pdpGetData'}, shopDomain=prod.shop_domain, productKey=prod.name_domain, cb_kwargs={'shop_alias': prod.shop_domain})

    def parse(self, response, shop_alias):
        data = response['pdpGetLayout']
        if data is None:
            return

        def find_component(name):
            component = [comp for comp in data['components']
                         if comp['name'] == name]
            if len(component) != 0:
                return component[0]
            else:
                return None

        content = find_component('product_content')['data'][0]
        name = content['name']
        price = content['price']['value']
        stock = content['stock']['value']

        detail = find_component('product_detail')['data'][0]['content']
        condition = [comp['subtitle']
                     for comp in detail if comp['title'] == 'Kondisi'][0]
        description = [comp['subtitle']
                       for comp in detail if comp['title'] == 'Deskripsi'][0]

        image_urls = [img['urlThumbnail'] for img in find_component(
            'product_media')['data'][0]['media'] if img['type'] == 'image']

        basic_info = data['basicInfo']
        menu = basic_info['menu']
        categories = basic_info['category']['detail']

        stats = basic_info['stats']
        sold = basic_info['txStats']['countSold']

        yield TokpedProduct({
            "id": basic_info['id'],
            "alias": basic_info['alias'],
            "name": name,
            "price": price,
            "description": description,
            "weight": basic_info['weight'],
            "menu_id": menu['id'],
            "menu_name": menu['name'],
            "min_order": basic_info['minOrder'],
            "max_order": basic_info['maxOrder'],
            "condition": condition,
            "stock": stock,
            "url": basic_info['url'],

            "shop_name": basic_info['shopName'],
            "shop_alias": shop_alias,
            "shop_id": basic_info['shopID'],

            "main_category": categories[-2]['name'],
            "sub_category": categories[-1]['name'],

            "view_count": stats['countView'],
            "review_count": stats['countReview'],
            "talk_count": stats['countTalk'],
            "rating": stats['rating'],
            "sold": sold,

            "image_urls": image_urls
        })

    gql = TokpedGQL("PDPGetLayoutQuery", query="""
fragment ProductMedia on pdpDataProductMedia { media { type urlThumbnail: URLThumbnail } } fragment ProductHighlight on pdpDataProductContent { name price { value currency } stock { value } } fragment ProductCustomInfo on pdpDataCustomInfo { icon title isApplink applink separator description } fragment ProductInfo on pdpDataProductInfo { row content { title subtitle } } fragment ProductDetail on pdpDataProductDetail { content { title subtitle } } fragment ProductDataInfo on pdpDataInfo { icon title isApplink applink content { icon text } } query PDPGetLayoutQuery($shopDomain: String, $productKey: String, $layoutID: String, $apiVersion: Float, $userLocation: pdpUserLocation!) { pdpGetLayout(shopDomain: $shopDomain, productKey: $productKey, layoutID: $layoutID, apiVersion: $apiVersion, userLocation: $userLocation) { name pdpSession basicInfo { alias id: productID shopID shopName minOrder maxOrder weight weightUnit condition status url needPrescription catalogID isLeasing isBlacklisted menu { id name url } category { id name title breadcrumbURL detail { id name breadcrumbURL } } txStats { countSold } stats { countView countReview countTalk rating } } components { name type position data { ...ProductMedia ...ProductHighlight ...ProductInfo ...ProductDetail ...ProductDataInfo ...ProductCustomInfo } } } }
""", default_variables={
        # "shopDomain": "kiosmatraman",
        # "productKey": "susu-dyco-colostrum-isi-30-saset",
        "layoutID": "",
        "apiVersion": 1,
        "userLocation": {
            "addressID": "0",
            "districtID": "2274",
            "postalCode": "",
            "latlon": ""
        }
    }
    )


class TokpedWeightScraper(scrapy.Spider, BaseSpiderGQL):
    name = 'tokped_products_weight'

    def __init__(self, product_list):
        self.product_list = read_df(product_list)[
            ['id', 'alias', 'shop_alias']]

    def start_requests(self):
        for i, prod in self.product_list.iterrows():
            yield self.gql.request_old(callback=self.parse_split, headers={'x-tkpd-akamai': 'pdpGetData'}, shopDomain=prod.shop_alias, productKey=prod.alias)

    def parse(self, response):
        data = response['pdpGetLayout']
        if data is None:
            return
        basic_info = data['basicInfo']
        weight = basic_info['weight']
        weight_unit = basic_info['weightUnit']
        weight = calculate_weight(weight, weight_unit)

        yield {
            'id': basic_info['id'],
            'weight': weight
        }

    gql = TokpedGQL("PDPGetLayoutQuery", query="""
fragment ProductMedia on pdpDataProductMedia { media { type urlThumbnail: URLThumbnail } } fragment ProductHighlight on pdpDataProductContent { name price { value currency } stock { value } } fragment ProductCustomInfo on pdpDataCustomInfo { icon title isApplink applink separator description } fragment ProductInfo on pdpDataProductInfo { row content { title subtitle } } fragment ProductDetail on pdpDataProductDetail { content { title subtitle } } fragment ProductDataInfo on pdpDataInfo { icon title isApplink applink content { icon text } } query PDPGetLayoutQuery($shopDomain: String, $productKey: String, $layoutID: String, $apiVersion: Float, $userLocation: pdpUserLocation!) { pdpGetLayout(shopDomain: $shopDomain, productKey: $productKey, layoutID: $layoutID, apiVersion: $apiVersion, userLocation: $userLocation) { name pdpSession basicInfo { alias id: productID shopID shopName minOrder maxOrder weight weightUnit condition status url needPrescription catalogID isLeasing isBlacklisted menu { id name url } category { id name title breadcrumbURL detail { id name breadcrumbURL } } txStats { countSold } stats { countView countReview countTalk rating } } components { name type position data { ...ProductMedia ...ProductHighlight ...ProductInfo ...ProductDetail ...ProductDataInfo ...ProductCustomInfo } } } }
""", default_variables={
        # "shopDomain": "kiosmatraman",
        # "productKey": "susu-dyco-colostrum-isi-30-saset",
        "layoutID": "",
        "apiVersion": 1,
        "userLocation": {
            "addressID": "0",
            "districtID": "2274",
            "postalCode": "",
            "latlon": ""
        }
    }
    )
