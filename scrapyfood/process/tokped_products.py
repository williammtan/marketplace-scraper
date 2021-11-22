
import os
import json
import logging
import argparse
import jsonlines
import numpy as np
import pandas as pd
from tqdm import tqdm
import math


from process.base_process import BaseProcess, scrape
from scrapyfood.spiders.tokped_search import TokpedSearchScraper
from scrapyfood.spiders.tokped_similar import TokpedSimilarScraper
from scrapyfood.utils import read_df
from nlp.keyword import find_keywords

BASE_QUERY = [
    {
        "id": "q",
        "name": "query",
    },
    {
        "id": "ob",
        "name": "order_by",
                "values": [
                    {
                        "name": "Paling Sesuai",
                        "value": "23"
                    },
                    {
                        "name": "Ulasan",
                        "value": "5"
                    },
                    {
                        "name": "Terbaru",
                        "value": "9"
                    },
                    {
                        "name": "Harga Tertinggi",
                        "value": "4"
                    },
                    {
                        "name": "Harga Terendah",
                        "value": "3"
                    }
                ],
        "type": "parameter"
    },
]


class TokpedProcess(BaseProcess):
    def __init__(self, main_category, categories_file, output_dir):
        self.main_category = main_category
        self.output_dir = output_dir
        self.categories_file = open(categories_file)
        self.sub_categories = [cat for cat in json.load(
            self.categories_file) if cat['id'] == self.main_category][0]['child']

    def start(self):
        """
        Pipeline:
            1. search category
            2. find and search keywords
            3. search individual products, and get related
        """
        fname_output = os.path.join(self.output_dir, 'products.jsonlines')
        related_output = os.path.join(self.output_dir, 'related.jsonlines')

        scrape(TokpedSearchScraper, self.create_settings(
            fname_output=fname_output
        ), query_file=self.create_search_query(category_mapping=[{"name": sub_cat['name'], "value": sub_cat['id']} for sub_cat in self.sub_categories], ob=False))

        search_keywords = find_keywords(read_df(fname_output))
        logging.info(f'Found keywords: {search_keywords}')
        scrape(TokpedSearchScraper, self.create_settings(
            fname_output=fname_output
        ), query_file=self.create_search_query(queries=[{'name': f'keyword {i}', 'value': k} for i, k in enumerate(search_keywords)]))  # add new keywords to product file and process
        self.process_df(fname=fname_output)

        self.batch_scrape(df_fname=fname_output, scrape_func=lambda df: scrape(TokpedSimilarScraper, self.create_settings(
            fname_output=fname_output), product_list=df), batch_size=10000)

        # self.scrape_product_search(fname_output, related_output)
        self.batch_scrape(df_fname=fname_output, scrape_func=lambda df: scrape(TokpedSearchScraper, self.create_settings(
            fname_output=fname_output
        ), query_file=self.create_search_query(queries=[{'name': f'product {i}', 'value': k} for i, k in enumerate(df.name)], ob=False),
            related_output=related_output, max_queries=2000
        ), sample_size=50000)

        with jsonlines.open(related_output) as reader:
            related_keywords = np.unique(list(reader))
        scrape(TokpedSearchScraper, self.create_settings(
            fname_output=fname_output
        ), query_file=self.create_search_query(queries=[{'name': f'keyword {i}', 'value': k} for i, k in enumerate(related_keywords)], ob=False), max_queries=3000)  # add new related keywords to product file and process
        self.process_df(fname=fname_output)

    def batch_scrape(self, df_fname, scrape_func, sample_size=None, batch_size=2000):
        sample_df = read_df(df_fname)
        sample_size = sample_size or len(sample_df)
        sample_df = sample_df.sample(sample_size)
        iterations = math.floor(sample_size / batch_size)
        tqdm_bar = tqdm(total=sample_size)
        for i in tqdm(range(iterations)):
            # eg. i=0, df[0:3000], i=2, df[6000:9000]
            process_df = sample_df[i*batch_size: (i+1)*batch_size]

            scrape_func(process_df)

            tqdm_bar.update((i+1)*batch_size)
            self.process_df(fname=df_fname)
        tqdm_bar.close()

    def scrape_product_search(self, df_fname, related_output, sample_size=40000, batch_size=2000):
        """Searches a sample of products, and processes in batches, each time deleting duplicates in the file"""
        sample_df = read_df(df_fname).sample(sample_size)
        iterations = math.floor(sample_size / batch_size)
        tqdm_bar = tqdm(total=sample_size)
        for i in tqdm(range(iterations)):
            # eg. i=0, df[0:3000], i=2, df[6000:9000]
            process_df = sample_df[i*batch_size: (i+1)*batch_size]

            scrape(TokpedSearchScraper, self.create_settings(
                fname_output=df_fname
            ), query_file=self.create_search_query(queries=[{'name': f'product {i}', 'value': k} for i, k in enumerate(process_df.name)], ob=False),
                related_output=related_output, max_queries=1000
            )
            tqdm_bar.update((i+1)*batch_size)
            self.process_df(fname=df_fname)
        tqdm_bar.close()

    def _process_df(self, df):
        return df[df.sub_category.isin([cat['identifier'] for cat in self.sub_categories])]

    # category_mapping=[{"name": "Keju", "value": "2722"}, {"name": "Krim", "value": "2724"}]
    def create_search_query(self, queries=None, category_id=None, category_mapping=None, ob=True):
        query = BASE_QUERY.copy()

        def select_from_query(param, is_paramter=True):
            parameter = [q for q in query if q['id'] == param]
            if len(parameter) == 0:
                # create paramter
                query.append({'id': param, 'name': param})
                parameter = query[-1]
            else:
                parameter = parameter[0]

            if is_paramter:
                parameter['type'] = 'parameter'
            else:
                parameter['type'] = 'setting'
            return parameter

        if not ob:
            select_from_query('ob', is_paramter=False)['value'] = "23"

        if not category_mapping:
            # constant category
            category_id = category_id or self.main_category  # defaults to self.main_category
            select_from_query('sc', is_paramter=False)['value'] = category_id
        else:
            select_from_query('sc', is_paramter=True)[
                'values'] = category_mapping

        if not queries:
            # delete parameter
            query_index = [i for i, q in enumerate(query) if q['id'] == 'q'][0]
            # if len(query_index) != 0:
            query.pop(query_index)
        else:
            select_from_query('q')['values'] = queries

        return query


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--main-cat', required=True,
                        help='Main category id to scrape')
    parser.add_argument('-c', '--categories', required=True,
                        help='Path to categories JSON file', default='../categories.json')
    parser.add_argument('-o', '--dir', required=True,
                        help='Output directory')
    parser.add_argument('-rt', '--rating', default='4,5')

    args = parser.parse_args()

    if not os.path.isdir(args.dir):
        os.makedirs(args.dir)

    process = TokpedProcess(args.main_cat, args.categories, args.dir)
    process.start()
