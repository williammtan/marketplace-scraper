set -e # exit on error

cd scrapyfood

datetime=$(date +"%Y%m%d")
run_dir="../data/runs/"
mkdir -p "$run_dir"

scraper_input="$run_dir/scraper_input.csv"
scraper_output="$run_dir/products.jsonlines"

bq query --format=csv --max_rows=30000 --use_legacy_sql=false '
    SELECT *
    FROM `food-id-app.external_data_temp.EXTERNAL_CATEGORIES`
    ' > $scraper_input

pip3 install -r requirements.txt

scrapy crawl tokped_category_growth -a categories=$scraper_input -O $scraper_output

blob="gs://data_external_backup/upload/category-updates/$datetime/categories.jsonlines"
gsutil cp $scraper_output $blob
bq load \
  --replace \
  --source_format="NEWLINE_DELIMITED_JSON" \
  "external_data_temp.EXTERNAL_CATEGORIES_GROWTH_$datetime" \
  $blob \
  ../product_schema.json

gcloud logging write scraper-log "Completed category-growth-scraper update with $(wc -l < $preprocessing_output) categories"

