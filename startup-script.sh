
cd /home/externalscraper/food_scraping/
git stash
git pull

chmod +x product-scraper.sh
./product-scraper.sh

chmod +x product-scraper-full.sh
./product-scraper-full.sh

chmod +x category-growth-scraper.sh
./category-growth-scraper.sh

gcloud logging write scraper-log "Completed all startup-script tasks"
