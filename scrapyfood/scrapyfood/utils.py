import re
import json
import pandas as pd
from scrapy.utils.project import get_project_settings


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


def read_df(file):
    file_type = file.split('.')[-1]
    if file_type == 'json':
        df = pd.read_json(file)
    elif file_type == 'jsonlines':
        df = pd.read_json(file, lines=True)
    elif file_type == 'csv':
        df = pd.read_csv(file)
    else:
        raise Exception('Unknown file type')

    df['id'] = df['id'].apply(str)
    return df
