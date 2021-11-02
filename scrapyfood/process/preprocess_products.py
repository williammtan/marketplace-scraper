import pandas as pd
import numpy as np
import random
import argparse
import os
import datetime
from tqdm import tqdm
import jsonlines

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

col_conversions = {
    'id': int,
    'price': int,
    'strike_price': int,
    'discount': float,
    'weight': int,
    'menu_id': int,
    'min_order': int,
    'max_order': int,
    'stock': int,
    'wholesale_quantity': int,
    'wholesale_price': int,
    'shop_id': int,
    'view_count': int,
    'review_count': int,
    'talk_count': int,
    'rating': float,
    'sold': int,
    'transactions': int
}

def process_external_temp(args):

    df = read_df(args.products)  # from search

    df['strike_price'] = df.strike_price.astype('int64')

    df = df.drop(columns=['image_urls'])

    # add times
    df['created_at'] = args.time
    df['updated_at'] = args.time

    # convert nans to pd.Int32Dtype
    df['wholesale_price'] = df.wholesale_price.astype(pd.Int32Dtype())
    df['wholesale_quantity'] = df.wholesale_quantity.astype(pd.Int32Dtype())

    # save to file
    df.to_json(args.output,
               lines=True, orient='records')

def process_external_temp_gen(args):
    """Preprocess using generator loop instead of loading full into memory"""
    with jsonlines.open(args.products) as reader:
        with jsonlines.open(args.output, 'w') as writer:
            for row in tqdm(reader):
                row['created_at'] = args.time
                row['updated_at'] = args.time

                for k,t in col_conversions.items():
                    if row[k] is not None:
                        row[k] = t(row[k])

                del row['strike_price']
                del row['image_urls']
                writer.write(row)
                


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--products')
    parser.add_argument('-t', '--time', default=get_date_time())
    parser.add_argument('-o', '--output')
    # parser.add_argument('-m', '--media', default=False, action='store_true')
    args = parser.parse_args()

    process_external_temp_gen(args)


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
