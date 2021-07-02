
# cd /home/externalscraper-vm/food_scraping/
git pull
# mode=$1

chmod +x product-scraper.sh
./product-scraper.sh

# if [ "$mode" = "products" ]
# then
#     chmod +x product-scraper.sh
#     ./product-scraper.sh
# elif [ "$mode" = "shops" ]
# then
#     chmod +x shop-scraper.sh
#     ./shop-scraper.sh
# else
#     echo "ERROR: unknown argument for mode, (available products | shops)"
# fi