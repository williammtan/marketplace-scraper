import scrapy
import pandas as pd
import json
import re
import csv

class TokpedSpider(scrapy.Spider):
    name = 'tokped'
    AUTOTHROTTLE_ENABLED = True

    def start_requests(self):
        df_urls = pd.read_csv("../data/fulllink_tokped_2.csv")
        urls = df_urls['url'].to_list()
        urls = ['https://www.tokopedia.com/sejahtera888/pure-baking-soda-arm-hammer-500-gram?src=topads',
            'https://www.tokopedia.com/ezybakingshop/mercolade-rainbow-compound-repack-per-batang-coklat-blok-warna-warn-pink-strawberry?src=topads',
            'https://www.tokopedia.com/houseoforganix/vanilla-extract?whid=0',
            'https://www.tokopedia.com/tokobahankuedona/diamond-dark-chocolate-compound-repack-245-255gr-cokelat-diamond?src=topads'
        ]
        for l in urls:
            yield scrapy.Request(url=l, callback=self.parse)

    def parse(self, response):
        df = {}

        nama = response.xpath('//h1[@class="css-v7vvdw"]/text()').get()
        infokat = response.css('.css-yoyor-unf-heading.e1qvo2ff7::text').getall()
        terjual_raw = response.xpath('//script//text()').getall()
        # terjual = terjual_raw[5]
        terjual = str(terjual_raw)
        terjual = terjual[terjual.find('"itemSoldPaymentVerified"'):]
        terjual = terjual[:terjual.find(',')]
        terjual = terjual.split('"')
        rating = response.xpath('//meta[@itemprop="ratingValue"]/@content').get()
        ulasan = response.xpath('//meta[@itemprop="ratingCount"]/@content').get()
        harga = response.xpath('//div[@data-testid="lblPDPDetailProductPrice"]/text()').get()
        hargaawal = response.xpath('//span[@data-testid="lblPDPDetailOriginalPrice"]/text()').get()
        diskon = response.xpath('//span[@data-testid="lblPDPDetailDiscountPercentage"]/text()').get()
        stok = response.xpath('//div[@data-testid="quantityOrder"]//p//b/text()').get()
        kondisiberat = response.xpath('//li[@class="css-1vbldqk"]//span[@class="main"]/text()').getall()
        subkatetalase = response.xpath('//li[@class="css-1vbldqk"]//a//b/text()').getall()
        desc = response.xpath('//div[@data-testid="lblPDPDescriptionProduk"]/text()').getall()
        outlet = response.xpath('//title/text()').get()
        outlet = outlet.split(" - ")
        outlet = outlet[-1]
        outlet = outlet[:outlet.find(" | Tokopedia")]
        url = response.xpath('//meta[@property="og:url"]/@content').get()

        df['nama_produk'] = nama
        df['terjual'] = terjual[3]
        df['rating'] = rating
        df['ulasan'] = ulasan
        df['harga'] = harga
        df['harga_awal'] = hargaawal
        df['diskon'] = diskon
        df['stok'] = stok
        df['kondisi'] = kondisiberat[0]
        df['berat'] = kondisiberat[1]
        df['kategori'] = infokat[2]
        df['sub_kategori'] = subkatetalase[0]
        df['etalase'] = subkatetalase[1]
        df['desc'] = desc
        df['outlet'] = outlet
        # df['area_pengiriman'] = outlet
        df['url'] = url

        yield df
