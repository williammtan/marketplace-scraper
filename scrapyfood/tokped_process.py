
import os
import json
import logging
import argparse
import numpy as np
import pandas as pd


from base_process import BaseProcess, scrape
from scrapyfood.spiders.tokped_search import TokpedSearchScraper
from scrapyfood.spiders.tokped_similar import TokpedSimilarScraper
from nlp.keyword import find_keywords


class TokpedProcess(BaseProcess):
    categories_file = open('../data/tokped/categories.json')

    def __init__(self, main_category, output_dir):
        self.main_category = main_category
        self.output_dir = output_dir
        self.sub_categories = [cat for cat in json.load(
            self.categories_file) if cat['id'] == self.main_category][0]['sub_categories']

    def start(self):
        for sub_cat in self.sub_categories:
            self.scrape_sub_category(sub_cat)

    def scrape_sub_category(self, sub_category):
        """
        Scrape sub category, steps:
            1. Search category
            2. Similar products
            3. Search common keywords
        """
        output_dir = os.path.join(self.output_dir, sub_category['name'])
        search_fname = os.path.join(output_dir, 'search.jsonline')
        similar_fname = os.path.join(output_dir, 'similar.jsonline')
        keyword_fname = os.path.join(output_dir, 'keyword.jsonline')

        scrape(TokpedSearchScraper, self.create_settings(fname_output=search_fname), query_file={
            'category': sub_category['id']
        })

        scrape(TokpedSimilarScraper, self.create_settings(
            fname_output=similar_fname), product_list=search_fname)

        # search_keywords = find_keywords()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--main-cat', required=True,
                        help='Main category id to scrape')
    parser.add_argument('-d', '--dir', required=True, help='Output directory')
    # parser.add_argument('-s', '--settings', required=False,
    #                     help='Additional settings overide')

    args = parser.parse_args()

    if not os.path.isdir(args.dir):
        os.makedirs(args.dir)

    process = TokpedProcess(args.main_cat, args.dir)
    process.start()
