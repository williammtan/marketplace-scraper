#!/bin/bash
set -e # exit on error

cd scrapyfood

datetime=$(date +"%Y%m%d")
run_dir="../data/runs/"
mkdir -p "$run_dir"

scraper_input="$run_dir/scraper_input.csv"
scraper_output="$run_dir/products.jsonlines"
preprocessing_output="$run_dir/products.preprocessed.jsonlines"

bq query --format=csv --max_rows=30000000 --use_legacy_sql=false 'SELECT
  products.id, products.alias, shop.id, shop.alias as shop_alias
  FROM (`food-id-app.external_data_temp.EXTERNAL_SHOPS` shop
  INNER JOIN
  `food-id-app.external_data_temp.EXTERNAL_PRODUCTS_PARETO` products
  ON shop.id = products.shop_id
    )' > $scraper_input

pip3 install -r requirements.txt

scrapy crawl tokped_products -a product_list="$run_dir/scraper_input.csv" -O "$run_dir/products.jsonlines"
python3 -m process.preprocess_products -p $scraper_output -o $preprocessing_output

blob="gs://data_external_backup/upload/updates/$datetime/products.jsonlines"
raw_blob="gs://data_external_backup/upload/updates/$datetime/products_raw.jsonlines"
gsutil cp $preprocessing_output $blob
gsutil cp "$run_dir/products.jsonlines" $raw_blob
bq load \
  --replace \
  --source_format="NEWLINE_DELIMITED_JSON" \
  "external_data_temp.EXTERNAL_PRODUCTS_ANALYTICS_$datetime" \
  $blob \
  ../product_schema.json

gcloud logging write scraper-log "Completed product-scraper update with $(wc -l < $preprocessing_output) products"

