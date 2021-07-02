
cd scrapyfood

datetime=$(date +"%Y%m%d")
run_dir="../data/runs/$datetime-products"
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

blob="gs://data_external_backup/upload/updates/datetime/products.jsonlines"
gsutil cp $preprocessing_output $blob
bq load \
  --source_format="NEWLINE_DELIMITED_JSON" \
  "external_data_temp.EXTERNAL_PRODUCTS_ANALYTICS_TEST_$datetime" \
  $blob \
  ../product_schema.json

