import argparse
import datetime
import os
import platform
import sys
import time

from web_scraping_food import ingest_tokopedia_link, ingest_tokopedia_desc, ingest_tokopedia
from user_agent import list_test

parser = argparse.ArgumentParser()
parser.add_argument('--headers_list_test', action='store_true', help='test list of headers')
parser.add_argument('--ingest_tokopedia_link', action='store_true', help='ingest link tokopedia')
parser.add_argument('--ingest_tokopedia_desc', action='store_true', help='ingest description tokopedia product based on link')
parser.add_argument('--ingest_tokopedia', action='store_true', help='process all tokopedia ingestion')
args = parser.parse_args()

if __name__ == '__main__':
    if args.headers_list_test:
        list_test()

    if args.ingest_tokopedia_link:
        ingest_tokopedia_link()
    elif args.ingest_tokopedia_desc:
        ingest_tokopedia_desc()
    elif args.ingest_tokopedia:
        ingest_tokopedia()
