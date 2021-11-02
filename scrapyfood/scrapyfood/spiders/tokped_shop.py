import re
import json
import scrapy
from datetime import datetime
from ..gql import TokpedGQL, BaseSpiderGQL
from ..items import TokpedShopCoreItem, TokpedShopStatisticItem, TokpedShopSpeedItem


class TokpedShopCoreScraper(BaseSpiderGQL, scrapy.Spider):
    name = 'tokped_shop_core'

    def __init__(self, shop_domains):
        if type(shop_domains) == str:
            f = open(shop_domains)
            shop_domains = json.load(f)
        self.shop_domains = shop_domains

    def start_requests(self):
        for dom in self.shop_domains:
            yield self.gql.request_old(callback=self.parse_split, domain=dom)

    def parse(self, response):
        data = response['shopInfoByID']['result'][0]
        shop_core = data['shopCore']
        shop_stats = data['shopStats']

        # eg. August 2017 - MONTH YEAR
        started_at_str = data['createInfo']['openSince']
        started_at_timestamp = datetime.strptime(started_at_str, '%B %Y')

        yield TokpedShopCoreItem({
            "id": shop_core['shopID'],
            "name": shop_core['name'],
            "alias": shop_core['domain'],
            "description": shop_core['description'],
            "tagline": shop_core['tagLine'],
            "active_products": data['activeProduct'],
            "location": data['location'],
            "is_closed": data['statusInfo']['shopStatus'] != 1,

            "products_sold": shop_stats['productSold'],
            "transaction_count": shop_stats['totalTxSuccess'],
            "favourite_count": data['favoriteData']['totalFavorite'],

            "started_at": started_at_timestamp.strftime('%Y-%m'),
        })

    gql = TokpedGQL(operation_name='ShopInfoCore', query="""
    query ShopInfoCore($id: Int!, $domain: String) {
  shopInfoByID(input: {shopIDs: [$id], fields: ["active_product", "address", "allow_manage_all", "assets", "core", "closed_info", "create_info", "favorite", "location", "status", "is_open", "other-goldos", "shipment", "shopstats", "shop-snippet", "other-shiploc", "shopHomeType"], domain: $domain, source: "shoppage"}) {
    result {
      shopCore {
        description
        domain
        shopID
        name
        tagLine
        defaultSort
        __typename
      }
      createInfo {
        openSince
        __typename
      }
      favoriteData {
        totalFavorite
        alreadyFavorited
        __typename
      }
      activeProduct
      shopAssets {
        avatar
        cover
        __typename
      }
      location
      isAllowManage
      isOpen
      address {
        name
        id
        email
        phone
        area
        districtName
        __typename
      }
      shipmentInfo {
        isAvailable
        image
        name
        product {
          isAvailable
          productName
          uiHidden
          __typename
        }
        __typename
      }
      shippingLoc {
        districtName
        cityName
        __typename
      }
      shopStats {
        productSold
        totalTxSuccess
        totalShowcase
        __typename
      }
      statusInfo {
        shopStatus
        statusMessage
        statusTitle
        __typename
      }
      closedInfo {
        closedNote
        until
        reason
        __typename
      }
      bbInfo {
        bbName
        bbDesc
        bbNameEN
        bbDescEN
        __typename
      }
      goldOS {
        isGold
        isGoldBadge
        isOfficial
        badge
        shopTier
        __typename
      }
      shopSnippetURL
      customSEO {
        title
        description
        bottomContent
        __typename
      }
      __typename
    }
    error {
      message
      __typename
    }
    __typename
  }
}""", default_variables={
        "id": 0,
        #   "domain": "tltsn"
    })


class TokpedShopStatisticScraper(BaseSpiderGQL, scrapy.Spider):
    name = 'tokped_shop_statistic'

    def __init__(self, shop_ids):
        if type(shop_ids) == str:
            shop_ids = json.load(open(shop_ids))
        self.shop_ids = shop_ids

    def start_requests(self):
        for id in self.shop_ids:
            yield self.gql.request_old(callback=self.parse_split, shopID=int(id), cb_kwargs={'id': id})

    def parse(self, response, id):
        satisfaction = response['shopSatisfaction']['recentOneMonth']
        rating = response['shopRating']
        shop_reputation = response['shopReputation'][0]
        badge = shop_reputation['badge'].split('/')[-1].split('.')[0]
        rep_score = int(re.sub("[^0-9]", "", shop_reputation['score']))
        yield TokpedShopStatisticItem({
            "id": id,
            "satisfaction": {
                "bad": satisfaction['bad'],
                "neutral": satisfaction['neutral'],
                "good": satisfaction['good']
            },
            "rating": {
                "score": rating['ratingScore'],
                "review_count": rating['totalReview'],
                "one_star": rating['detail']['oneStar']['totalReview'],
                "two_star": rating['detail']['twoStar']['totalReview'],
                "three_star": rating['detail']['threeStar']['totalReview'],
                "four_star": rating['detail']['fourStar']['totalReview'],
                "five_star": rating['detail']['fiveStar']['totalReview'],
            },
            "reputation": {
                "badge": badge,
                "score_level": shop_reputation['score_map'],
                "score": rep_score
            }
        })

    gql = TokpedGQL(operation_name='ShopStatisticQuery', query="""
    query ShopStatisticQuery($shopID: Int!) {
  shopSatisfaction: ShopSatisfactionQuery(shopId: $shopID) {
    recentOneMonth {
      bad
      good
      neutral
      __typename
    }
    __typename
  }
  shopRating: ShopRatingQuery(shopId: $shopID) {
    detail {
      oneStar {
        rate
        totalReview
        percentageWord
        percentage
        __typename
      }
      twoStar {
        rate
        totalReview
        percentageWord
        percentage
        __typename
      }
      threeStar {
        rate
        totalReview
        percentageWord
        percentage
        __typename
      }
      fourStar {
        rate
        totalReview
        percentageWord
        percentage
        __typename
      }
      fiveStar {
        rate
        totalReview
        percentageWord
        percentage
        __typename
      }
      __typename
    }
    starLevel
    ratingScore
    totalReview
    __typename
  }
  shopReputation: reputation_shops(shop_ids: [$shopID]) {
    badge
    score
    score_map
    __typename
  }
}""")


class TokpedShopSpeedScraper(BaseSpiderGQL, scrapy.Spider):
    name = 'tokped_shop_speed'

    def __init__(self, shop_ids):
        if type(shop_ids) == str:
            shop_ids = json.load(open(shop_ids))
        self.shop_ids = shop_ids

    def start_requests(self):
        for id in self.shop_ids:
            yield self.gql.request_old(callback=self.parse_split, shopId=id, cb_kwargs={'id': id})

    def parse(self, response, id):
        yield TokpedShopSpeedItem({
            "id": id,
            "response_speed": response['shopSpeed']['messageResponseTime']
        })

    gql = TokpedGQL(operation_name='shopSpeedQuery', query="""
    query shopSpeedQuery($shopId: Int!) {
  shopSpeed: ProductShopChatSpeedQuery(shopId: $shopId) {
    messageResponseTime
    __typename
  }
}
""")
