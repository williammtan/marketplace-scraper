import scrapy
from ..utils import read_df, calculate_weight
from ..items import TokpedProduct
from ..gql import BaseSpiderGQL, TokpedGQL
import logging


class TokpedProductScraper(BaseSpiderGQL, scrapy.Spider):
    name = 'tokped_products'

    def __init__(self, product_list):
        self.product_list = read_df(product_list)
        if 'prod_url' in self.product_list.columns:
            if 'shop_alias' not in self.product_list.columns:
                self.product_list['shop_alias'] = self.product_list.apply(
                    lambda x: x.prod_url.split('/')[-2], axis=1)
            if 'alias' not in self.product_list.columns:
                self.product_list['alias'] = self.product_list.apply(
                    lambda x: x.prod_url.split('/')[-1].split('?')[0], axis=1)

    def start_requests(self):
        for i, prod in self.product_list.iterrows():
            yield self.gql.request_old(callback=self.parse_split, headers={'x-tkpd-akamai': 'pdpGetData'}, shopDomain=prod.shop_alias, productKey=prod.alias, cb_kwargs={'shop_alias': prod.shop_alias})

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
        campaign = content['campaign']
        wholesale = content['wholesale']
        if len(wholesale) == 0:
            wholesale_quantity = None
            wholesale_price = None
        else:
            wholesale = wholesale[0]
            wholesale_quantity = wholesale['minQty']
            wholesale_price = wholesale['price']['value']

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

        if categories[0]['id'] != "35":
            logging.debug('Dropped item, not food.')
            return

        stats = basic_info['stats']
        tx_stats = basic_info['txStats']

        yield TokpedProduct({
            "id": basic_info['id'],
            "alias": basic_info['alias'],
            "name": name,

            "price": price,
            "strike_price": campaign['originalPrice'] if campaign['originalPrice'] != 0 else price,
            "discount": campaign['percentageAmount'],

            "description": description,
            "weight": basic_info['weight'],
            "menu_id": menu['id'],
            "menu_name": menu['name'],
            "min_order": basic_info['minOrder'],
            "max_order": basic_info['maxOrder'],
            "condition": condition,
            "stock": stock,
            "url": basic_info['url'],

            "wholesale_quantity": wholesale_quantity,
            "wholesale_price": wholesale_price,

            # "shop_name": basic_info['shopName'],
            # "shop_alias": shop_alias,
            "shop_id": basic_info['shopID'],

            "main_category": categories[-2]['name'],
            "sub_category": categories[-1]['name'],

            "view_count": stats['countView'],
            "review_count": stats['countReview'],
            "talk_count": stats['countTalk'],
            "rating": stats['rating'],
            "sold": tx_stats['countSold'],
            "transactions": tx_stats['transactionSuccess'],

            "image_urls": image_urls
        })

    gql = TokpedGQL("PDPGetLayoutQuery", query="""
fragment ProductVariant on pdpDataProductVariant {
  errorCode
  parentID
  defaultChild
  sizeChart
  variants {
    productVariantID
    variantID
    name
    identifier
    option {
      picture {
        urlOriginal: url
        urlThumbnail: url100
        __typename
      }
      productVariantOptionID
      variantUnitValueID
      value
      hex
      __typename
    }
    __typename
  }
  children {
    productID
    price
    priceFmt
    optionID
    productName
    productURL
    picture {
      urlOriginal: url
      urlThumbnail: url100
      __typename
    }
    stock {
      stock
      isBuyable
      stockWording
      stockWordingHTML
      minimumOrder
      maximumOrder
      __typename
    }
    isCOD
    isWishlist
    campaignInfo {
      campaignID
      campaignType
      campaignTypeName
      campaignIdentifier
      background
      discountPercentage
      originalPrice
      discountPrice
      stock
      stockSoldPercentage
      threshold
      startDate
      endDate
      endDateUnix
      appLinks
      isAppsOnly
      isActive
      hideGimmick
      isCheckImei
      __typename
    }
    thematicCampaign {
      additionalInfo
      background
      campaignName
      icon
      __typename
    }
    __typename
  }
  __typename
}

fragment ProductMedia on pdpDataProductMedia {
  media {
    type
    urlThumbnail: URLThumbnail
    videoUrl: videoURLAndroid
    prefix
    suffix
    description
    __typename
  }
  videos {
    source
    url
    __typename
  }
  __typename
}

fragment ProductHighlight on pdpDataProductContent {
  name
  price {
    value
    currency
    __typename
  }
  campaign {
    campaignID
    campaignType
    campaignTypeName
    campaignIdentifier
    background
    percentageAmount
    originalPrice
    discountedPrice
    originalStock
    stock
    stockSoldPercentage
    threshold
    startDate
    endDate
    endDateUnix
    appLinks
    isAppsOnly
    isActive
    hideGimmick
    __typename
  }
  thematicCampaign {
    additionalInfo
    background
    campaignName
    icon
    __typename
  }
  stock {
    useStock
    value
    stockWording
    __typename
  }
  variant {
    isVariant
    parentID
    __typename
  }
  wholesale {
    minQty
    price {
      value
      currency
      __typename
    }
    __typename
  }
  isCashback {
    percentage
    __typename
  }
  isTradeIn
  isOS
  isPowerMerchant
  isWishlist
  isCOD
  isFreeOngkir {
    isActive
    __typename
  }
  preorder {
    duration
    timeUnit
    isActive
    preorderInDays
    __typename
  }
  __typename
}

fragment ProductCustomInfo on pdpDataCustomInfo {
  icon
  title
  isApplink
  applink
  separator
  description
  __typename
}

fragment ProductInfo on pdpDataProductInfo {
  row
  content {
    title
    subtitle
    applink
    __typename
  }
  __typename
}

fragment ProductDetail on pdpDataProductDetail {
  content {
    title
    subtitle
    applink
    showAtFront
    isAnnotation
    __typename
  }
  __typename
}

fragment ProductDataInfo on pdpDataInfo {
  icon
  title
  isApplink
  applink
  content {
    icon
    text
    __typename
  }
  __typename
}

fragment ProductSocial on pdpDataSocialProof {
  row
  content {
    icon
    title
    subtitle
    applink
    type
    rating
    __typename
  }
  __typename
}

query PDPGetLayoutQuery($shopDomain: String, $productKey: String, $layoutID: String, $apiVersion: Float, $userLocation: pdpUserLocation!) {
  pdpGetLayout(shopDomain: $shopDomain, productKey: $productKey, layoutID: $layoutID, apiVersion: $apiVersion, userLocation: $userLocation) {
    name
    pdpSession
    basicInfo {
      alias
      id: productID
      shopID
      shopName
      minOrder
      maxOrder
      weight
      weightUnit
      condition
      status
      url
      needPrescription
      catalogID
      isLeasing
      isBlacklisted
      menu {
        id
        name
        url
        __typename
      }
      category {
        id
        name
        title
        breadcrumbURL
        isAdult
        detail {
          id
          name
          breadcrumbURL
          isAdult
          __typename
        }
        __typename
      }
      blacklistMessage {
        title
        description
        button
        url
        __typename
      }
      txStats {
        transactionSuccess
        transactionReject
        countSold
        paymentVerified
        itemSoldPaymentVerified
        __typename
      }
      stats {
        countView
        countReview
        countTalk
        rating
        __typename
      }
      __typename
    }
    components {
      name
      type
      position
      data {
        ...ProductMedia
        ...ProductHighlight
        ...ProductInfo
        ...ProductDetail
        ...ProductSocial
        ...ProductDataInfo
        ...ProductCustomInfo
        ...ProductVariant
        __typename
      }
      __typename
    }
    __typename
  }
}

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


class TokpedWeightScraper(BaseSpiderGQL, scrapy.Spider):
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


class TokpedTransactionScraper(BaseSpiderGQL, scrapy.Spider):
    name = 'tokped_products_transaction'

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
        stats = basic_info['txStats']

        yield {
            'id': basic_info['id'],
            'sold': stats['countSold'],
            'payment_verified': stats['paymentVerified'],
            'item_sold_payment_verified': stats['itemSoldPaymentVerified'],
            'transaction_success': stats['transactionSuccess'],
            'transaction_reject': stats['transactionReject']
        }

    gql = TokpedGQL("PDPGetLayoutQuery", query="""

query PDPGetLayoutQuery($shopDomain: String, $productKey: String, $layoutID: String, $apiVersion: Float, $userLocation: pdpUserLocation!) {
  pdpGetLayout(shopDomain: $shopDomain, productKey: $productKey, layoutID: $layoutID, apiVersion: $apiVersion, userLocation: $userLocation) {
    basicInfo {
      id: productID
      txStats {
        transactionSuccess
        transactionReject
        countSold
        paymentVerified
        itemSoldPaymentVerified
        __typename
      }
    }
}
}
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
