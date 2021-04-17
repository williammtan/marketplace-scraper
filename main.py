import argparse
import datetime
import os
import platform
import sys
import time

from web_scraping_food import ingest_tokopedia_link, ingest_tokopedia_desc, ingest_tokopedia_full, ingest_bukalapak_full, ingest_shopee_full, \
ingest_tokopedia_outlet, ingest_tokopedia_desc_full
from user_agent import list_test

parser = argparse.ArgumentParser()
parser.add_argument('--headers_list_test', action='store_true', help='test list of headers')
parser.add_argument('--ingest_tokopedia_link', action='store_true', help='ingest link tokopedia')
parser.add_argument('--ingest_tokopedia_desc', action='store_true', help='ingest description tokopedia product based on link')
parser.add_argument('--ingest_tokopedia_full', action='store_true', help='process all tokopedia ingestion')
parser.add_argument('--ingest_tokopedia_outlet', action='store_true', help='ingest tokopedia outlet')
parser.add_argument('--ingest_tokopedia_desc_full', action='store_true', help='process all detail product tokopedia')
parser.add_argument('--ingest_bukalapak_full', action='store_true', help='ingest bukalapak')
parser.add_argument('--ingest_shopee', action='store_true', help='ingest shopee')
parser.add_argument('--ingest_shopee_full', action='store_true', help='ingest shopee full')
args = parser.parse_args()

if __name__ == '__main__':
    if args.headers_list_test:
        list_test()

    if args.ingest_tokopedia_link:
        ingest_tokopedia_link()
    elif args.ingest_tokopedia_desc:
        ingest_tokopedia_desc()
    elif args.ingest_tokopedia_full:
        ingest_tokopedia_full()
    elif args.ingest_tokopedia_outlet:
        ingest_tokopedia_outlet()
    elif args.ingest_tokopedia_desc_full:
        ingest_tokopedia_desc_full()

    elif args.ingest_bukalapak_full:
        ingest_bukalapak_full()
    
    elif args.ingest_shopee_full:
        ingest_shopee_full()
    
