import re
import os
import json
import pandas as pd
import logging
from tqdm import tqdm
from scrapy.utils.project import get_project_settings
from subprocess import check_output
from .constants import tokped_search_params

CHUNKSIZE = 20000
MIN_LINES_ITER = 100000


def get_cache(html):
    data = html.css("body > script:nth-child(5)::text").get()
    start_index = re.search("window.__cache=", data).end()
    end_index = re.search('}};', data).end() - 1  # end index of dict
    cache = data[start_index:end_index]  # eg: 667:384807
    cache_data = json.loads(cache)  # convert json to dict=
    return cache_data


def fix_appended_json(file):
    with open(file, 'r') as f:
        text = f.read()
        if file.endswith('.jsonlines'):
            text = text.replace('\n][', '')
        elif file.endswith('.json'):
            text = text.replace('\n][', ',')

    with open(file, 'w') as f:
        f.write(text)


def wc(filename):
    return int(check_output(["wc", "-l", filename]).split()[0])


def read_df(file):
    file_type = file.split('.')[-1]
    if file_type == 'json':
        df = pd.read_json(file)
    elif file_type == 'jsonlines':
        line_count = wc(file)
        if line_count > MIN_LINES_ITER:
            logging.info("Reading a large file, using chunks: ")
            df_iter = pd.read_json(file, lines=True, chunksize=CHUNKSIZE)
            df = pd.concat(
                [d for d in tqdm(df_iter, total=round(line_count/CHUNKSIZE))])
        else:
            df = pd.read_json(file, lines=True)
    elif file_type == 'csv':
        df = pd.read_csv(file)
    else:
        raise Exception('Unknown file type')

    # df['id'] = df['id'].apply(str)
    return df


def read_terjual_tokped(labels):
    text = [label['title']
            for label in labels if label['position'] == 'integrity']
    if len(text) == 0:
        # never sold any products
        return 0
    text = text[0]

    # eg "Terjual 795", "Terjual 2,5 rb", "Terjual 134 rb"
    base = float(''.join(re.findall(r'[\d,]', text)).replace(',', '.'))
    is_thousand = re.search(r'rb', text)
    if is_thousand:
        base *= 1000

    return int(base)


def read_rp_tokped(text):
    # eg. Rp.103.600
    if text:
        return int(''.join(re.findall(r'\d', text)))


# eg. {'sc': 2722, 'ob': 23} => device=desktop&rows=200&source=universal&sc=2722&ob=23
def create_tokped_params(params: dict):
    return tokped_search_params + '&'.join([f'{key}={val["value"]}' for key, val in params.items()])


def calculate_weight(weight, weight_unit):
    # weight_unit: GRAM | KILOGRAM
    if weight_unit == 'KILOGRAM':
        weight *= 1000
    return weight
