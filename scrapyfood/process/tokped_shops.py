import os
import json
import logging
import argparse
import numpy as np
import pandas as pd
from tqdm import tqdm


from process.base_process import BaseProcess, scrape
from scrapyfood.spiders.tokped_shop import TokpedShopCoreScraper, TokpedShopStatisticScraper, TokpedShopSpeedScraper
from scrapyfood.utils import read_df


class TokpedProcess(BaseProcess):
    def __init__(self, shops_df, output_dir):  # dataframe containing columns: id, domain
        self.shops_df = shops_df
        self.output_dir = output_dir

    def start(self):
        """
        Steps:
        1. scrape core
        2. scrape statistic
        3. scrape speed
        4. merge dfs and save file
        """
        core_fname = os.path.join(self.output_dir, 'core.jsonlines')
        stats_fname = os.path.join(self.output_dir, 'stats.jsonlines')
        speed_fname = os.path.join(self.output_dir, 'speed.jsonlines')
        shops_fname = os.path.join(self.output_dir, 'shops.jsonlines')

        scrape(TokpedShopCoreScraper, self.create_settings(
            fname_output=core_fname, overide=True
        ), shop_domains=self.shops_df.alias.to_list())

        scrape(TokpedShopStatisticScraper, self.create_settings(
            fname_output=stats_fname, overide=True
        ), shop_ids=self.shops_df.id.to_list())

        scrape(TokpedShopSpeedScraper, self.create_settings(
            fname_output=speed_fname, overide=True
        ), shop_ids=self.shops_df.id.to_list())

        self.merge(core_fname)
        self.merge(stats_fname)
        self.merge(speed_fname)

        self.shops_df.to_json(shops_fname, lines=True, orient='records')

    def merge(self, fname):
        df = read_df(fname)
        df['id'] = pd.to_numeric(df.id)
        self.shops_df['id'] = pd.to_numeric(self.shops_df.id)
        if 'alias' in df.columns:
            df = df.drop(columns='alias')
        self.shops_df = pd.merge(self.shops_df, df, on='id')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--shops-file', required=False,
                        help='File with unique shops\' id and alias')
    parser.add_argument('-p', '--products-file', required=False,
                        help='File with product\'s shop_id and shop_alias')
    parser.add_argument('-o', '--output-dir', required=True,
                        help='Output directory')
    parser.add_argument('-t', '--test', required=False, action='store_true',
                        help='Is a test run')
    args = parser.parse_args()

    if not os.path.isdir(args.output_dir):
        os.makedirs(args.output_dir)

    if args.shops_file:
        shops_df = read_df(args.shops_file)
        shops_df = shops_df[['id', 'alias']]
    elif args.products_file:
        products = read_df(args.products_file)
        shops_df = products[['shop_id', 'shop_alias']
                            ].drop_duplicates(subset='shop_id')
        shops_df.columns = ['id', 'alias']
    else:
        raise argparse.ArgumentError(
            "Arguments must include either --shops-file or --products-file argument")

    if args.test:
        shops_df = shops_df.sample(1000)

    process = TokpedProcess(shops_df, args.output_dir)
    process.start()
