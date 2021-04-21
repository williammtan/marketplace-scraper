import scrapy


class TokpedImagesSpider(scrapy.Spider):
    name = 'tokped_images'
    # start_urls = ['https://www.tokopedia.com/sejahtera888/pure-baking-soda-arm-hammer-500-gram?src=topads']
    
    def start_requests(self):
        # df_urls = pd.read_csv("../data/fulllink_tokped_3.csv")
        # urls = df_urls['url'].to_list()
        urls = ['https://www.tokopedia.com/sejahtera888/pure-baking-soda-arm-hammer-500-gram?src=topads',
            'https://www.tokopedia.com/ezybakingshop/mercolade-rainbow-compound-repack-per-batang-coklat-blok-warna-warn-pink-strawberry?src=topads',
            'https://www.tokopedia.com/houseoforganix/vanilla-extract?whid=0',
            'https://www.tokopedia.com/tokobahankuedona/diamond-dark-chocolate-compound-repack-245-255gr-cokelat-diamond?src=topads'
        ]
        for l in urls:
            yield scrapy.Request(url=l, callback=self.parse)

    def parse(self, response):
        # raw_image_urls = response.css('.image img::attr(src)').getall()
        names = response.xpath('//h1[@class="css-v7vvdw"]/text()').get()
        raw_image_urls  = response.xpath('//meta[@property="og:image"]/@content').getall()
        clean_image_urls = []
        for img_url in raw_image_urls:
            clean_image_urls.append(response.urljoin(img_url))

        yield {
            'image_names': names,
            'image_urls': clean_image_urls
        }
