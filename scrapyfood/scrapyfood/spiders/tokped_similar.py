
import pandas as pd
import scrapy
from ..utils import read_df
from ..gql import TokpedGQL, BaseSpiderGQL
from ..items import TokpedSimilarProduct


class TokpedSimilarScrape(scrapy.Spider, BaseSpiderGQL):
    name = 'tokped_similar'

    def __init__(self, product_list):
        self.df = read_df(product_list)

    def start_requests(self):
        for _, prod in self.df.iterrows():
            yield self.gql.request_old(callback=self.parse_split, cb_kwargs={'ref_id': prod.id}, productIDs=prod.id)

    def parse(self, response, ref_id):
        data = response['productRecommendationWidget']
        sections = data['data']
        for sect in sections:
            ref = {'from': ref_id, 'section': sect['title']}

            products = sect['recommendation']
            for prod in products:
                id = prod['id']
                name = prod['productName']
                category_breadcrumb = prod['categoryBreadcrumbs']
                prod_url = prod['productUrl']
                old_price = prod['slashedPriceInt']
                discounted_price = prod['priceInt']
                discount_percent = prod['productDiscountPercentage']
                stock = prod['stock']
                shop = prod['shop']
                image_urls = [prod['productImageUrl']]

                rating = prod['productRating']
                review_count = prod['productReviewCount']

                yield TokpedSimilarProduct({
                    'id': id,
                    'name': name,
                    'category_breadcrumb': category_breadcrumb,
                    'prod_url': prod_url,
                    'old_price': old_price,
                    'discounted_price': discounted_price,
                    'discount_percent': discount_percent,
                    'stock': stock,
                    'shop': shop,
                    'image_urls': image_urls,

                    'rating': rating,
                    'review_count': review_count,

                    'ref': ref
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
    }, request_cue_length=2)
