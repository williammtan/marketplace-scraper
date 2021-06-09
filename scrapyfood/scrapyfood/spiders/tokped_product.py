from os import read
import scrapy
from ..utils import read_df
from ..items import TokpedProduct
from ..gql import BaseSpiderGQL, TokpedGQL


class TokpedProductScraper(scrapy.Spider, BaseSpiderGQL):
    name = 'tokped_products'

    def __init__(self, product_list):
        self.product_list = read_df(product_list)
        print(self.product_list)

    def start_requests(self):
        for i, prod in self.product_list.iterrows():
            yield self.gql.request_old(self.parse_split, shopDomain=prod.shop_name, productKey=prod.name)

    def parse(self, response):
        return response['pdpGetLayout']

    gql = TokpedGQL("PDPGetLayoutQuery", query="""fragment ProductVariant on pdpDataProductVariant {
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

query PDPGetLayoutQuery(
	$shopDomain: String
	$productKey: String
	$layoutID: String
	$apiVersion: Float
	$userLocation: pdpUserLocation!
) {
	pdpGetLayout(
		shopDomain: $shopDomain
		productKey: $productKey
		layoutID: $layoutID
		apiVersion: $apiVersion
		userLocation: $userLocation
	) {
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
