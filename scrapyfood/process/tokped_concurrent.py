from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from scrapyfood.utils import read_df
from scrapyfood.spiders.tokped_product import TokpedProductScraper
import numpy as np
import argparse
import os


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file-input')
    parser.add_argument('-o', '--output')
    parser.add_argument('-c', '--concurrent-runs', type=int)
    args = parser.parse_args()
    output_dir = os.path.dirname(args.output)

    s = get_project_settings()

    settings = {
        'FEEDS': {
            args.output: {
                'format': args.output.split('.')[-1],
            },
        },
        'IMAGES_STORE': os.path.join(output_dir, 'images')
    }
    s.update(settings)

    print(s)
    configure_logging(s)
    process = CrawlerProcess(s)

    df = read_df(args.file_input)
    df_splits = np.array_split(df, args.concurrent_runs)

    df_split_folder = os.path.join(output_dir, 'splits')
    if not os.path.isdir(df_split_folder):
        os.makedirs(df_split_folder)

    for i, dataframe in enumerate(df_splits):
        df_name = 'products_split_' + str(i+1) + '.jsonlines'
        df_output = os.path.join(df_split_folder, df_name)
        if not os.path.isfile(df_output):
            dataframe.to_json(df_output, orient='records', lines=True)
        process.crawl(TokpedProductScraper, product_list=df_output)

    process.start()
