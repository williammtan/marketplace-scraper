
### SHOPEE ###

# api bases
shopee_search_api = 'https://shopee.co.id/api/v4/search/search_items?&by={search_by}&limit=100&match_id={match_id}&&page_type_search&newest={newest}&order={order}&'
shopee_prod_api = 'https://shopee.co.id/api/v2/item/get?itemid={id}&shopid={shop_id}'
shopee_similar_api = 'https://shopee.co.id/api/v4/recommend/recommend?catid={category_id}&item_card=3&itemid={id}&limit={limit}&offset=0&shopid={shop_id}&bundle=product_detail_page'

# url bases
shopee_prod_url = 'https://shopee.co.id/{name}-i.{shop_id}.{id}'
shopee_image_url = 'http://cf.shopee.co.id/file/{id}'

# proxy
proxy_url = "http://scraperapi:5b7afb62c67de1477c5359799c6d3607@proxy-server.scraperapi.com:8001"
