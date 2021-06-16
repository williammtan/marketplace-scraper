import pandas as pd
import numpy as np
import random
import argparse
import os
import datetime

from scrapyfood.utils import read_df


def id_generator():
    return random.randint(1000000000, 9999999999)  # random 10 digit number


def get_date_time():
    time_now = datetime.datetime.now(tz=datetime.timezone.utc)
    time_format = '%Y-%m-%d %H:%M:%S'
    time_string = time_now.strftime(time_format) + ' UTC'

    return time_string


def process_external(args):
    ### products ###

    df_short = read_df(os.path.join(
        args.dir, 'products.jsonlines'))  # from search
    df_full = read_df(os.path.join(
        args.dir, 'products_full.jsonlines'))  # individual

    # drop fields already in full
    df_short = df_short[['id', 'old_price', 'discount_percent']]
    df_full = df_full.drop(columns=[
        'alias', 'menu_id', 'shop_name', 'shop_alias', 'min_order', 'max_order', 'talk_count'])

    df = pd.merge(df_short, df_full, on='id')
    df = df.rename(
        {"id_y": "id", "shop_id": "external_outlet_id", "review_count": "review_number", "old_price": "strike_price", "discount_percent": "discount", "main_category": "category", "sub_category": "subcategory", "menu_name": "etalase"}, axis=1)

    time_string = get_date_time()
    df['created_at'] = time_string
    df['update_at'] = time_string

    for col in ['id', 'external_outlet_id', 'name', 'sold', 'rating', 'review_number', 'price', 'strike_price', 'discount',
                'stock', 'condition', 'weight', 'category', 'subcategory', 'etalase', 'url', 'created_at', 'update_at', 'view_count']:
        assert col in df.columns

    # eg. bumbu-bahan-masakan.csv
    # add a / to the end
    dirname = args.dir if args.dir[-1] == '/' else args.dir + '/'
    prod_filename = os.path.join(dirname, os.path.basename(
        os.path.dirname(dirname)) + '.csv')

    ### media ###

    df_images = []
    for i, prod in df_full.iterrows():
        for img in prod['images']:
            df_images.append({
                "id": id_generator(),
                "product_id": prod['id'],
                "media_path": img,
                "created_at": time_string,
                "update_at": time_string
            })
    df_images = pd.DataFrame(df_images)
    media_filename = os.path.join(dirname, 'media.csv')

    df = df.drop(columns=['image_urls', 'images'])

    df.to_csv(prod_filename)
    df_images.to_csv(media_filename)


def process_external_temp(args):

    df_short = read_df(os.path.join(
        args.dir, 'products.jsonlines'))  # from search
    df_full = read_df(os.path.join(
        args.dir, 'product_transactions.jsonlines'))  # individual
    print('done loading')

    # drop fields already in full
    df_short = df_short[['id', 'old_price', 'discount_percent']]
    # df = pd.merge(df_short, df_full, on='id')
    df = df_full.merge(df_short, on='id', how='left')
    print('done mergin')
    del df_full
    df['old_price'] = df.apply(lambda x: x.price if np.isnan(
        x.old_price) else x.old_price, axis=1)
    print('done old price')
    df['discount_percent'] = df.apply(lambda x: 0.0 if np.isnan(
        x.discount_percent) else x.discount_percent, axis=1)
    print('done discount')
    df = df.drop(columns=['shop_name', 'shop_alias'])  # already have shop_id
    df = df.rename(columns={'old_price': 'strike_price',
                   'discount_percent': 'discount'})
    print('done drop and rename')
    df['strike_price'] = df.strike_price.astype('int64')

    # make media
    if args.media:
        df_images = []
        for i, prod in df_full.iterrows():
            for url, img in zip(prod['image_urls'], prod['images']):
                df_images.append({
                    "id": id_generator(),
                    "product_id": prod['id'],
                    "media_path": img,
                    "media_url": url
                })
        df_images = pd.DataFrame(df_images)
        df = df.drop(columns='images')

    col_order = ['id', 'name', 'alias', 'description', 'weight', 'shop_id', 'price', 'strike_price', 'discount', 'url', 'menu_id', 'menu_name', 'min_order',
                 'max_order', 'condition', 'stock', 'main_category', 'sub_category', 'sold', 'transactions', 'view_count', 'review_count', 'rating', 'talk_count', 'created_at', 'updated_at']
    df = df.drop(columns=['image_urls'])

    # add times
    time_string = get_date_time()
    df['created_at'] = time_string
    df['updated_at'] = time_string

    df = df[col_order]
    print('done reorder columns')

    # save to file
    save_dir = os.path.join(args.dir, 'biquery')
    if not os.path.isdir(save_dir):
        os.makedirs(save_dir)
    df.to_json(os.path.join(save_dir, 'products.jsonlines'),
               lines=True, orient='records')

    if args.media:
        df_images['created_at'] = time_string
        df_images['updated_at'] = time_string
        df_images.to_json(os.path.join(save_dir, 'media.jsonlines'),
                          lines=True, orient='records')
    # df.to_csv(os.path.join(save_dir, 'products.csv'))
    # df_images.to_csv(os.path.join(save_dir, 'media.csv'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir')
    parser.add_argument('-m', '--media', default=False, action='store_true')
    args = parser.parse_args()
    assert os.path.isdir(args.dir)

    process_external_temp(args)


"""
### BIQEURY SCHEMA ###

id	INTEGER	
external_outlet_id	INTEGER	
name	STRING	
description	STRING	
sold	INTEGER	
rating	FLOAT	
review_number	INTEGER	
price	INTEGER	
strike_price	INTEGER	
discount	INTEGER	
stock	INTEGER	
condition	STRING	
weight	INTEGER	
category	STRING	
subcategory	STRING	
etalase	STRING	
url	STRING	
created_at	TIMESTAMP	
update_at	TIMESTAMP	
view_count	INTEGER	

[
    {
        "name": "id",
        "type": "INTEGER",
        "mode": "REQUIRED"
    },
    {
        "name": "alias",
        "type": "STRING",
        "mode": "REQUIRED"
    },
    {
        "name": "name",
        "type": "STRING",
        "mode": "REQUIRED"
    },
    {
        "name": "description",
        "type": "STRING",
        "mode": "NULLABLE"
    },
    {
        "name": "weight",
        "type": "INTEGER",
        "mode": "REQUIRED"
    },
    {
        "name": "shop_id",
        "type": "INTEGER",
        "mode": "REQUIRED"
    },
    {
        "name": "price",
        "type": "INTEGER",
        "mode": "REQUIRED"
    },
    {
        "name": "strike_price",
        "type": "INTEGER",
        "mode": "NULLABLE"
    },
    {
        "name": "discount",
        "type": "FLOAT",
        "mode": "NULLABLE"
    },
    {
        "name": "url",
        "type": "STRING",
        "mode": "REQUIRED"
    },
    {
        "name": "menu_id",
        "type": "INTEGER",
        "mode": "REQUIRED"
    },
    {
        "name": "menu_name",
        "type": "STRING",
        "mode": "REQUIRED"
    },
    {
        "name": "min_order",
        "type": "INTEGER",
        "mode": "NULLABLE"
    },
    {
        "name": "max_order",
        "type": "INTEGER",
        "mode": "NULLABLE"
    },
    {
        "name": "condition",
        "type": "STRING",
        "mode": "NULLABLE"
    },
    {
        "name": "stock",
        "type": "INTEGER",
        "mode": "NULLABLE"
    },
    {
        "name": "main_category",
        "type": "STRING",
        "mode": "NULLABLE"
    },
    {
        "name": "sub_category",
        "type": "STRING",
        "mode": "NULLABLE"
    },
    {
        "name": "sold",
        "type": "INTEGER",
        "mode": "NULLABLE"
    },
    {
        "name": "view_count",
        "type": "INTEGER",
        "mode": "NULLABLE"
    },
    {
        "name": "review_count",
        "type": "INTEGER",
        "mode": "NULLABLE"
    },
    {
        "name": "rating",
        "type": "FLOAT",
        "mode": "NULLABLE"
    },
    {
        "name": "talk_count",
        "type": "INTEGER",
        "mode": "NULLABLE"
    },
    {
        "name": "created_at",
        "type": "DATETIME",
        "mode": "NULLABLE"
    },
    {
        "name": "updated_at",
        "type": "DATETIME",
        "mode": "NULLABLE"
    }
]

### SCRAPY SCHEMA ###

class TokpedProduct(scrapy.Item):
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

"""
