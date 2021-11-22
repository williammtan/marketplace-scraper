#!/bin/bash

# scrapes categories
set -e
FEEDS=$1
echo $FEEDS

mkdir -p $FEEDS

shift
for cat in "$@"
do
    echo "running category: $cat"
    cat=$(echo $cat | tr -d '"')
    category_dir="$FEEDS/$cat"
    mkdir -p $category_dir
    python -m process.tokped_products -m $cat -o $category_dir
    scrapy crawl tokped_products -a product_list=$category_dir/products.jsonlines -s LOG_LEVEL='INFO' -o $category_dir/products_full.jsonlines
done
