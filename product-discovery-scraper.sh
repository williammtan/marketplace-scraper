
set -e # exit on error

cd scrapyfood

datetime=$(date +"%Y%m%d")

run_dir="../data/runs-discovery/"
current_products_file="$run_dir/products_current.csv"
new_products_file="$run_dir/products.csv"
new_products_full_file="$run_dir/products_full.jsonlines"
new_products_preprocessed_file="$run_dir/products.preprocessed.jsonlines"

rm -rf "$run_dir"
mkdir -p "$run_dir"

bq query --format=csv --max_rows=300000000 --use_legacy_sql=false '
SELECT
  id, url as prod_url
  FROM `food-id-app.external_data_temp.EXTERNAL_PRODUCTS` LIMIT 5
' > $current_products_file

IFS=' ' read -ra CATS <<< $(cat ../categories.json | jq '. | map(.id) | join (" ")' | tr -d '"')
for cat in "${CATS[@]}"
do
    echo "running category: $cat"
    cat=$(echo "$cat" | tr -d '"')
    category_dir="$run_dir/$cat"
    mkdir -p $category_dir
    # python -m process.tokped_products -m $cat -o $category_dir
    echo '
    {"id": 1, "prod_url": "https://www.tokopedia.com/hpmkemang/hoki-beras-5kg?whid=0"}
    {"id": 2, "prod_url": "https://www.tokopedia.com/delifarma/beras-bogor-rojolele-5-kg-25-kg-5-kg?whid=0"}
    ' > "$category_dir/products.jsonlines"
done

python -m process.merge_products $(find $run_dir -name "products.jsonlines") $current_products_file -c id prod_url -o $new_products_file
scrapy crawl tokped_products -a product_list=$new_products_file -s LOG_LEVEL='INFO' -o $new_products_full_file
python -m process.preprocess_products -p $new_products_full_file -o $new_products_preprocessed_file

blob="gs://data_external_backup/upload/updates-discovery/$datetime/products.jsonlines"
raw_blob="gs://data_external_backup/upload/updates-discovery/$datetime/products_raw.jsonlines"
gsutil cp $new_products_preprocessed_file $blob
gsutil cp $new_products_file $raw_blob
bq load \
  --replace \
  --source_format="NEWLINE_DELIMITED_JSON" \
  "external_data_temp.EXTERNAL_PRODUCTS_UPDATE" \
  $blob \
  ../product_schema.json
