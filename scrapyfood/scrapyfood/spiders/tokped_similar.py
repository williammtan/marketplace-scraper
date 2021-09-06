
import pandas as pd
import scrapy
from ..utils import read_df, read_terjual_tokped
from ..gql import TokpedGQL, BaseSpiderGQL
from ..items import TokpedShortProduct
import re
import json


class TokpedSimilarScraper(BaseSpiderGQL, scrapy.Spider):
    name = 'tokped_similar'

    def __init__(self, product_list, settings={
        'sections': ['Lainnya di toko ini', 'Produk sponsor terkait', 'Pilihan lainnya untukmu'], "category": None
    }):
        if type(product_list) == str:
            self.df = read_df(product_list)
        else:
            self.df = product_list

        if type(settings) == str:
            settings = json.loads(open(settings, 'r').read())
        self.keep_sections = settings['sections']
        self.category = settings['category']

    def start_requests(self):
        for _, prod in self.df.iterrows():
            yield self.gql.request_old(callback=self.parse_split, cb_kwargs={'ref_id': prod.id}, productIDs=str(prod.id))

    def parse(self, response, ref_id):
        data = response['productRecommendationWidget']
        sections = [sect for sect in data['data']
                    if sect['title'] in self.keep_sections]
        for sect in sections:
            ref = {'from': ref_id, 'section': sect['title']}

            products = sect['recommendation']
            for prod in products:
                id = prod['id']
                name = prod['productName']
                category_breadcrumb = prod['categoryBreadcrumbs']
                if self.category is not None and self.category not in category_breadcrumb.split('/'):
                    # if specific category is defined and it's not in the category breadcrumbs, skip
                    continue
                prod_url = prod['productUrl']
                old_price = prod['slashedPriceInt']
                discounted_price = prod['priceInt']
                discount_percent = prod['productDiscountPercentage']
                stock = prod['stock']
                shop = prod['shop']
                image_urls = [prod['productImageUrl']]

                rating = prod['productRating']
                review_count = prod['productReviewCount']
                sold = read_terjual_tokped(prod['productLabelGroups'])

                sub_category = category_breadcrumb.split('/')[-1]
                sub_category_lower = '-'.join([split for split in re.split(
                    r" |\-|&", sub_category.lower()) if split != ''])

                yield TokpedShortProduct({
                    'id': id,
                    'name': name,
                    'category_breadcrumb': category_breadcrumb,
                    'prod_url': prod_url,
                    'old_price': old_price,
                    'discounted_price': discounted_price,
                    'discount_percent': discount_percent,
                    'stock': stock,
                    'shop': shop['id'],
                    'image_urls': image_urls,
                    'sold': sold,

                    'rating': rating,
                    'review_count': review_count,

                    'ref': ref,
                    'sub_category': sub_category_lower
                })

    gql = TokpedGQL(operation_name='RecomWidget', query="""query RecomWidget(
        $userID: Int!
        $pageName: String!
        $xSource: String!
        $xDevice: String!
        $productIDs: String
        $LayoutPageType: String
        $ref: String
        $categoryIDs: String
        $queryParam: String
    ) {
        productRecommendationWidget(
            userID: $userID
            pageName: $pageName
            xSource: $xSource
            xDevice: $xDevice
            productIDs: $productIDs
            LayoutPageType: $LayoutPageType
            ref: $ref
            categoryIDs: $categoryIDs
            queryParam: $queryParam
        ) {
            data {
                tID
                source
                title
                foreignTitle
                seeMoreUrlLink
                layoutType
                pageName
                widgetUrl
                recommendation {
                    originalPrice: slashedPrice
                    slashedPriceInt
                    productDiscountPercentage: discountPercentage
                    productReviewCount: countReview
                    isWishlist: isWishlist
                    productImageUrl: imageUrl
                    isTopads
                    clickUrl
                    trackerImageUrl
                    productUrl: url
                    productRating: rating
                    productPrice: price
                    priceInt
                    id
                    productName: name
                    categoryBreadcrumbs
                    recommendationType
                    stock
                    departmentID: departmentId
                    shop {
                        id
                        name
                        location
                        city
                        url
                        __typename
                    }
                    productLabels: labels {
                        title
                        color
                        __typename
                    }
                    productLabelGroups: labelgroup {
                        type
                        title
                        position
                        __typename
                    }
                    wholesalePrice {
                        price
                        quantityMax
                        quantityMin
                        priceString
                        __typename
                    }
                    badges {
                        title
                        imageUrl
                        __typename
                    }
                    __typename
                }
                __typename
            }
            meta {
                recommendation
                size
                failSize
                processTime
                experimentVersion
                __typename
            }
            __typename
        }
    }
    """, default_variables={
        "userID": 0,
        "xDevice": "desktop",
        "xSource": "recom_widget",
        "pageName": "pdp_1,pdp_2,pdp_3,pdp_4",
        "ref": "",
        # "productIDs": "183203785",
        "categoryIDs": "",
        "LayoutPageType": "desktop",
        "queryParam": "user_addressId=0&user_cityId=176&user_districtId=2274&user_lat=&user_long=&user_postCode="
    })
