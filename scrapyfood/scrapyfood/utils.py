import re
import json


def get_cache(html):
    data = html.css("body > script:nth-child(5)::text").get()
    start_index = re.search("window.__cache=", data).end()
    end_index = re.search('}};', data).end() - 1  # end index of dict
    cache = data[start_index:end_index]  # eg: 667:384807
    cache_data = json.loads(cache)  # convert json to dict=
    return cache_data
