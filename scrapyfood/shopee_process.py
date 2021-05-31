# Given main category, script will scrape it

from enum import unique
import os
from re import search
from scrapyfood.utils import read_df
import time
import json
import argparse
import shutil
import pandas as pd

from scrapyfood.spiders.shopee_page import ShopeePageScraper
from scrapyfood.spiders.shopee_products import ShopeeProductScraper
from scrapyfood.spiders.shopee_similar import ShopeeSimilarScraper
from scrapyfood.constants import shopee_prod_api
from scrapy.utils.log import configure_logging
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from multiprocessing import Process, Queue
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests

import logging
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)


def scrape(spider, settings={}, *args, **kwargs):
    output_fname, output_settings = list(settings['FEEDS'].items())[0]
    if not output_settings['overwrite'] and os.path.isfile(output_fname):
        return

    logging.info(f'running {spider} spider')
    queue = Queue()
    process = Process(target=f, args=(
        queue, spider, settings, *args), kwargs=kwargs)
    process.start()
    result = queue.get()
    process.join()

    if result is not None:
        raise result


def f(queue, spider, settings, *args, **kwargs):
    try:
        s = get_project_settings()
        s.update(settings)
        configure_logging(s)

        runner = CrawlerRunner(s)
        defered = runner.crawl(spider, *args, **kwargs)
        defered.addBoth(lambda _: reactor.stop())
        time.sleep(1)
        reactor.run()
        queue.put(None)
    except Exception as e:
        queue.put(e)


class ShopeeProcess(object):
    def __init__(self, main_category, output_dir):
        """
        1. scrape main category and get all unique subcategory category names
        2. iterate unique subcategories and:
            a) scrape by all ordering and/or desc/acc (download images)
            b) save to files with {order}_{desc/acc}.json (eg. ctime_desc.json)
            c) scrape individual items (don't download images)
            d) save to files
            e) filter and delete not in category files
        3. concat all to final json

        final result:
            output_dir/
                main_category.json
                products.json
                12512/
                    images/*
                    search.json
                    similar.json
                12541/
                    images/*
                    search.json
                    similar.json
                12411/
                    images/*
                    search.json
                    similar.json
        """
        self.main_category = main_category
        self.output_dir = output_dir

        self.setup_webdriver()

    def start(self):
        try:
            save_categories_fname = os.path.join(
                self.output_dir, 'categories.json')
            if os.path.isfile(save_categories_fname):
                save_categories = open(save_categories_fname)
                self.sub_categories = json.load(save_categories)
            else:
                self.sub_categories = self.get_unique_categories()
                save_categories = open(save_categories_fname, 'w')
                print(self.sub_categories)
                json.dump(self.sub_categories, save_categories)

            for cat_id, cat_name in self.sub_categories.items():
                self.scrape_sub_category(cat_id, cat_name)

        except Exception as err:
            self.driver.close()
            raise err

    def setup_webdriver(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # headless browser
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        self.driver.get("https://www.google.com")

    def process_df(self, fname, short=True, main_cat=None, sub_cat=None):
        # short meaning, not individually scraped products
        """Drop duplicates, simplify categories, and save file"""
        image_folder = os.path.join(os.path.dirname(fname), 'images')

        df = read_df(fname)
        df = df.dropna(subset=df.columns.difference(['brand']))
        df = df.drop_duplicates(subset='id')
        not_df = pd.DataFrame(columns=df.columns)
        if not short:
            # get sub category available items and get sub + main categories
            df = df[df.apply(lambda x: len(x.categories) ==
                             3 and x.categories[2] is not None, axis=1)]
            df['main_category'] = df.apply(
                lambda x: x.categories[1]['name'], axis=1)
            df['sub_category'] = df.apply(
                lambda x: x.categories[2]['name'], axis=1)

            if main_cat:
                not_df = pd.concat([not_df, df[df.main_category != main_cat]])
            if sub_cat:
                not_df = pd.concat([not_df, df[df.sub_category != sub_cat]])

            # delete all images in not_df
            images = [os.path.join(image_folder, img)
                      for imgs in not_df.images.values for img in imgs]

            moved = 0
            for img in images:
                try:
                    os.remove(img)
                    moved += 1
                except FileNotFoundError:
                    logging.debug(
                        f"Couldn't remove file {img}, file not found")
            logging.info(
                f'Removed {moved} images from {image_folder}, {len(images) - moved} failed')

            df.drop(index=not_df.index)

        df = df.reset_index()
        df.to_json(fname)

    def scrape_sub_category(self, cat_id, cat_name):
        logging.info(f'scraping category {cat_id}')
        cat_dir = os.path.join(self.output_dir, cat_id)

        search_fname = os.path.join(cat_dir, 'search.jsonlines')
        similar_fname = os.path.join(cat_dir, 'similar.jsonlines')
        unique_fname = os.path.join(cat_dir, 'unique.json')
        full_prods_fname = os.path.join(cat_dir, 'full.json')

        self.scrape_category(category_id=cat_id,
                             fname_output=search_fname, save_imgs=True, overide=False)
        self.scrape_similar(search_fname, similar_fname,
                            save_imgs=True, overide=True)
        cat_df = read_df(search_fname)
        sim_df = read_df(similar_fname)
        unique_df = pd.concat([cat_df, sim_df]).drop_duplicates(
            subset='id').reset_index()
        unique_df.to_json(unique_fname)
        self.process_df(unique_fname, short=True)
        self.scrape_products(unique_fname, fname_output=full_prods_fname)
        self.process_df(full_prods_fname, short=False, main_cat=cat_name)

    def get_unique_categories(self):
        main_category_fname = os.path.join(
            self.output_dir, 'main_category.json')
        main_category_full_fname = os.path.join(
            self.output_dir, 'main_category_full.json')

        if not os.path.isfile(main_category_full_fname):
            self.scrape_category(category_id=self.main_category, fname_output=main_category_fname,
                                 save_imgs=False, filters=['rele'])  # scrape main category
            self.scrape_products(products_df=main_category_fname,
                                 fname_output=main_category_full_fname)

        main_category_df = pd.read_json(main_category_full_fname)

        main_category_df = main_category_df[main_category_df.apply(lambda x: len(
            x.categories) == 3 and x.categories[2] != None, axis=1)]  # remove items with no sub category
        main_category_df.sub_category = main_category_df.apply(
            lambda x: x.categories[2]['name'], axis=1)  # get sub category name
        unique_categories = main_category_df.sub_category.unique()

        sub_category_ids = {}

        for category in unique_categories:
            # get any item which has the category
            category_prod = main_category_df[main_category_df.sub_category == category]
            prod = category_prod.iloc[0]
            self.driver.get(prod.url)
            time.sleep(1)
            subcategory_element = self.driver.find_elements_by_class_name(
                '_3YDLCj')[-1]
            subcategory_element.click()
            sub_category_id = self.driver.current_url.split('.')[-1]
            # sub_category_ids.append(sub_category_id)

            self.driver.get(shopee_prod_api.format(
                id=prod.id, shop_id=prod.shop_id))

            prod_json = json.loads(
                self.driver.find_element_by_xpath('/html/body/pre').text)

            cat_name = prod_json['item']['categories'][-1]['display_name']
            sub_category_ids[sub_category_id] = cat_name

        return sub_category_ids

    def create_settings(self, fname_output, save_imgs, overide):
        output_dir = os.path.dirname(fname_output)
        item_pipeline = {
            'scrapyfood.pipelines.ImagePipeline': 1} if save_imgs else {}
        image_output = os.path.join(output_dir, 'images')

        settings = {
            'FEEDS': {
                fname_output: {
                    'format': fname_output.split('.')[-1],
                    'overwrite': overide
                },
            },
            'ITEM_PIPELINES': item_pipeline,
            'IMAGES_STORE': image_output
        }

        return settings

    def scrape_similar(self, products_df, fname_output, save_imgs=True, overide=True):
        settings = self.create_settings(fname_output, save_imgs, overide)

        scrape(ShopeeSimilarScraper, settings,
               product_list=products_df, query_count=20)

    def scrape_category(self, category_id, fname_output, save_imgs=True, filters=['sales', 'pop'], overide=True):
        """Scrape by category id"""
        settings = self.create_settings(fname_output, save_imgs, overide)

        for searchby in filters:
            scrape(ShopeePageScraper, settings,
                   category=category_id, searchby=searchby)

    def scrape_products(self, products_df, fname_output, overide=True):
        settings = self.create_settings(
            fname_output, save_imgs=False, overide=overide)

        scrape(ShopeeProductScraper, settings, product_list=products_df)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--main_cat', required=True,
                        help='Main category id to scrape')
    parser.add_argument('-d', '--dir', required=True, help='Output directory')
    # parser.add_argument('-s', '--settings', required=False,
    #                     help='Additional settings overide')

    args = parser.parse_args()

    if not os.path.isdir(args.dir):
        os.makedirs(args.dir)

    process = ShopeeProcess(args.main_cat, args.dir)
    process.start()
