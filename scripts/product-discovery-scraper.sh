#!/bin/bash
set -e # exit on error

cd scrapyfood

datetime=$(date +"%Y%m%d")

run_dir="../data/runs-discovery/"
current_products_file="$run_dir/products_current.csv"
new_products_file="$run_dir/products.csv"
current_table="food-id-app.external_data_temp.EXTERNAL_PRODUCTS"
temp_table="food-id-app.external_data_temp.EXTERNAL_PRODUCTS_UPDATE_TEMP"
update_table="food-id-app.external_data_temp.EXTERNAL_PRODUCTS_UPDATE"

rm -rf "$run_dir"
mkdir -p "$run_dir"


IFS=' ' read -ra CATS <<< $(cat ../categories.json | jq '. | map(.id) | join (" ")' | tr -d '"')
for cat in "${CATS[@]}"
do
    echo "running category: $cat"
    cat=$(echo "$cat" | tr -d '"')
    category_dir="$run_dir/$cat"
    mkdir -p $category_dir
    python3 -m process.tokped_products -m $cat -o $category_dir
done

python3 -m process.merge_products $(find $run_dir -name "products.jsonlines") -c id prod_url -o $new_products_file -r 'prod_url:url'

blob="gs://data_external_backup/upload/updates-discovery/$datetime/products.jsonlines"
gsutil cp $new_products_file $blob
bq load \
  --replace \
  --source_format="NEWLINE_DELIMITED_JSON" \
  $temp_table \
  $blob \
  ../product_schema.json

bq query \
    --replace \
    --destination_table $update_table \
    --use_legacy_sql=false \
    "
    SELECT id, url
    FROM $current_table

    UNION

    SELECT id, url
    FROM $temp_table
    " # union $current_table and $temp_table to $update_table

gcloud logging write scraper-log "Completed product-discovery-scraper update with $(wc -l < $new_products_preprocessed_file) products"
