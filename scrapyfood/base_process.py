import pandas as pd
import logging
import time
import os

from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from scrapyfood.utils import read_df

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from multiprocessing import Process, Queue
from twisted.internet import reactor


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


class BaseProcess:
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

    def create_settings(self, fname_output, save_imgs=False, overide=False):
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


class WebdriverProcess:
    def __init__(self):
        self.setup_webdriver()

    def setup_webdriver(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # headless browser
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        self.driver.get("https://www.google.com")
