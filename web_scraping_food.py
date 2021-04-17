import requests
import json
import bs4
import pandas as pd
import os
import csv
import time
import sys
import urllib.request
from datetime import date
import logging
# from htmldate import find_date
from dotenv import load_dotenv
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from json import JSONDecoder

from fake_useragent import UserAgent
from user_agent import random_header

load_dotenv()

def ingest_tokopedia_outlet():
    # set link from list
    df_raw = pd.read_csv('data/link_outlet_raw_1-4.csv')
    link = []

    for index, dt in df_raw.iterrows():
        link.append(dt[0])

    # set csv
    csv_file = open(f'data/link_outlet_tokped_1.csv', 'w', encoding='utf-8') 
    writer = csv.writer(csv_file)
    csv_file2 = open(f'data/info_outlet_tokped_1.csv', 'w', encoding='utf-8') 
    writer2 = csv.writer(csv_file2)

    df = {}
    df_ol = {}
    outlet_list = []

    # call open browser function
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    # chrome_options.headless = True
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--incognito')
    # set user agent
    ua = UserAgent()
    userAgent = ua.random
    chrome_options.add_argument(f'user-agent={userAgent}')
    driver = webdriver.Chrome("../chromedriver", options=chrome_options)

    for l in link:
        total_product = 0
        print(l)
        # open url
        driver.get(l)
        i = 1
        while i>0:  
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print("page ", i)
            try:
                time.sleep(2)
                outlet = driver.find_elements_by_xpath('.//div[@class="css-wlcnlb"]//div[@class="unf-card css-4fg9nr-unf-card e1ukdezh0"]//div[@class="pcv3__container css-1bd8ct"]//div[@class="css-1ehqh5q"]//a[@href]')
                total_product = total_product + len(outlet)
                for k in range(0, len(outlet)):
                    linklist = driver.find_elements_by_xpath('.//div[@class="css-wlcnlb"]//div[@class="unf-card css-4fg9nr-unf-card e1ukdezh0"]//div[@class="pcv3__container css-1bd8ct"]//div[@class="css-1ehqh5q"]//a[@href]')
                    url_w = linklist[k].get_attribute('href')
                    # print(url_w)
                    df['link'] = url_w
                    writer.writerow(df.values())
                
            except Exception as e:
                print("failed to get outlet", e)
                time.sleep(1)
                pass

            time.sleep(1)
            try:
                hha = driver.find_element_by_xpath('.//a[@data-testid="btnShopProductPageNext"]')
                i = i+1
                l2 = f'{l}/page/{i}'
                # print(l2)
                driver.get(l2)
            except Exception as e:
                print("Page has ended")
                # print(e)
                i = 0
                exit
        
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        try:
            name1 = driver.find_element_by_xpath('.//h1[@class="css-1i6886t"]')
            name = name1.text
        except:
            name = "-"
            pass
        
        try:
            sold1 = driver.find_element_by_xpath('.//h2[@class="css-lzwncz-unf-heading e1qvo2ff2"]')
            sold = sold1.text
        except:
            sold = "-"
            pass

        try:
            score1 = driver.find_element_by_xpath('.//h2[@class="css-rfs3ih-unf-heading e1qvo2ff2"]')
            score = score1.text
        except:
            score = "-"
            pass

        try:
            review1 = driver.find_element_by_xpath('.//h6[@class="css-1s96mum-unf-heading e1qvo2ff6"]')
            review = review1.text
        except:
            review = "-"
            pass
        
        try:
            area1 = driver.find_elements_by_xpath('.//p[@class="css-dxunmy-unf-heading e1qvo2ff8"]')
            area = area1[-1].text
        except:
            area = "-"
            pass
        
        try:
            follower1 = driver.find_element_by_xpath('.//h6[@class="css-jsut4p-unf-heading e1qvo2ff6"]')
            follower = follower1.text
        except:
            follower = "-"
            pass
        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        try:
            desc1 = driver.find_element_by_xpath('.//div[@class="css-1gp0czb epavnfa0"]//div[@class="css-1t40sc2 epavnfa1"]//p//span')
            desc = desc1.text
        except:
            desc = "-"
            pass
        
        try:
            since1 = driver.find_elements_by_xpath('.//div[@class="css-1gp0czb epavnfa0"]//div[@class="css-1t40sc2 epavnfa1"]//p')
            since = since1[-1].text #last tag
        except:
            since = "-"
            pass
        

        df_ol['total_produk'] = total_product
        df_ol['nama_outlet'] = name
        df_ol['produk_terjual'] = sold
        df_ol['score_outlet'] = score
        df_ol['ulasan'] = review
        df_ol['area'] = area
        df_ol['follower'] = follower
        df_ol['deskripsi_toko'] = desc
        df_ol['buka_sejak'] = since
        df_ol['url'] = l

        writer2.writerow(df_ol.values())

    driver.quit()

def ingest_tokopedia_desc_full():
    num = 1
    data = pd.read_csv(f"data/fulllink_tokped_{num}.csv")

    # set csv
    today = date.today()
    csv_file = open(f'data/tokped/fullproduk_tokped_{num}.csv', 'w', encoding='utf-8') 
    writer = csv.writer(csv_file)

    df = {}
    # call open browser function
    chrome_options = Options()
    # chrome_options.add_argument('--window-size=1920,1080')
    # chrome_options.headless = True
    # chrome_options.set_headless(headless=True)
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--incognito')
    driver = webdriver.Chrome("../chromedriver", options=chrome_options)

    for i, dt in enumerate(data['url'].items()):
        url = str(dt)
        print(i,"." , url)
        try:
            # open url
            driver.get(url)
            time.sleep(1)

            try:
                nama1 = driver.find_element_by_xpath('.//h1[@class="css-v7vvdw"]')
                nama = nama1.text
            except:
                nama = "-"
                pass

            try:
                terjual1 = driver.find_element_by_xpath('.//div[@data-testid="lblPDPDetailProductSoldCounter"]')
                terjual = terjual1.text
            except:
                terjual = "-"
                pass

            try:
                rating1 = driver.find_element_by_xpath('.//span[@data-testid="lblPDPDetailProductRatingNumber"]')
                rating = rating1.text
            except:
                rating = "-"
                pass
            
            try:
                ulasan1 = driver.find_element_by_xpath('.//span[@data-testid="lblPDPDetailProductRatingCounter"]')
                ulasan = ulasan1.text
            except:
                ulasan = "-"
                pass

            try:
                harga1 = driver.find_element_by_xpath('.//div[@data-testid="lblPDPDetailProductPrice"]')
                harga = harga1.text
            except:
                harga = "-"
                pass

            try:
                hargaawal1 = driver.find_element_by_xpath('.//span[@data-testid="lblPDPDetailOriginalPrice"]')
                hargaawal = hargaawal1.text
            except:
                hargaawal = "-"
                pass
            
            try:
                diskon1 = driver.find_element_by_xpath('.//span[@data-testid="lblPDPDetailDiscountPercentage"]')
                diskon = diskon1.text
            except:
                diskon = "-"
                pass

            try:
                stok1 = driver.find_element_by_xpath('.//div[@data-testid="quantityOrder"]//p//b')
                stok = stok1.text
            except:
                stok = "-"
                pass
            
            try:
                wenew1 = driver.find_elements_by_xpath('.//li[@class="css-1vbldqk"]//span[@class="main"]')
                kondisi = wenew1[0].text
                berat = wenew1[1].text
            except:
                kondisi = "-"
                berat = "-"
                pass

            try:
                subetas1 = driver.find_elements_by_xpath('.//li[@class="css-1vbldqk"]//a')
                subcat = subetas1[0].text
                etalase = subetas1[1].text
            except:
                subcat = "-"
                etalase = "-"
                pass

            try:
                desc1 = driver.find_element_by_xpath('.//div[@data-testid="lblPDPDescriptionProduk"]')
                desc = desc1.text
            except:
                desc = "-"
                pass

            try:
                outlet1 = driver.find_element_by_xpath('.//a[@data-testid="llbPDPFooterShopName"]')
                outlet = outlet1.text
            except:
                outlet = "-"
                pass
            
            df['nama'] = nama
            df['terjual'] = terjual
            df['rating'] = rating
            df['ulasan'] = ulasan
            df['harga'] = harga
            df['hargaawal'] = hargaawal
            df['diskon'] = diskon
            df['stok'] = stok
            df['kondisi'] = kondisi
            df['berat'] = berat
            df['subcat'] = subcat
            df['etalase'] = etalase
            df['desc'] = desc
            df['outlet'] = outlet
            df['url'] = url

            writer.writerow(df.values())

        except Exception as e:
            print("failed scrap the url", e)
            time.sleep(1)
            pass

    # exit the browser
    driver.quit()

def ingest_tokopedia_link(category):
    # category = 'kue'
    url = f'https://www.tokopedia.com/p/makanan-minuman/{category}?page=1&goldmerchant=true&official=true&ob=5&rt=4,5&ob=5'

    # set csv
    # today = date.today()
    csv_file = open(f'data/link_outlet_tokped_{category}.csv', 'w', encoding='utf-8') 
    writer = csv.writer(csv_file)
    df = {}
    total_all = 0
    
    # call open browser function
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.headless = True
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--incognito')
    # set user agent
    ua = UserAgent()
    userAgent = ua.random
    chrome_options.add_argument(f'user-agent={userAgent}')
    driver = webdriver.Chrome("../chromedriver", options=chrome_options)
    # open url
    driver.get(url)

    for i in range(1, 5):
        print(f"iterasi ke {i}")
        # time.sleep(10)
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            products = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, './/div[@class="css-bk6tzz e1nlzfl3"]//a[@href]')))
            # time.sleep(2)
            total = len(products)
            print(total)
            total_all += total
            # time.sleep(5)

            for k in range(0, total):
                try:
                    linklist = None
                    linklist = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, './/div[@class="css-bk6tzz e1nlzfl3"]//a[@href]')))
                    # time.sleep(2)
                    url_w = linklist[k].get_attribute('href')

                    if "ta.tokopedia.com" in url_w:
                        sa = url_w[url_w.find('www.tokopedia.com'):]
                        sa = sa.replace('%2F','/')
                        sa = sa[:sa.find('%3F')]
                        sa = sa.split('/')
                        sa = "https://www.tokopedia.com/" + sa[1]
                    else:
                        sa = url_w.split('/')
                        sa = "https://www.tokopedia.com/" + sa[3]

                    df['link'] = sa
                    writer.writerow(df.values())

                except Exception as e:
                    print("failed scrap", e)
                    time.sleep(1)
                    pass

        except Exception as e:
            print("failed to next page", e)
            time.sleep(1)
            pass

        j = i+1
        url2 = f'https://www.tokopedia.com/p/makanan-minuman/{category}?page={j}&goldmerchant=true&official=true&ob=5&rt=4,5&ob=5'
        driver.get(url2)

    print(total_all)
    driver.quit()

def ingest_tokopedia_desc(category):
    # category = "teh_2"
    data = pd.read_csv(f"data/link_tokped_{category}.csv")

    # set csv
    today = date.today()
    csv_file = open(f'data/link_tokped_{category}.csv', 'w', encoding='utf-8') 
    writer = csv.writer(csv_file)

    df = {}
    # call open browser function
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.headless = True
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--incognito')
    prefs = {"profile.managed_default_content_settings.images":2,
            "profile.default_content_setting_values.notifications":2,
            "profile.managed_default_content_settings.stylesheets":2,
            "profile.managed_default_content_settings.cookies":2,
            "profile.managed_default_content_settings.javascript":1,
            "profile.managed_default_content_settings.plugins":1,
            "profile.managed_default_content_settings.popups":2,
            "profile.managed_default_content_settings.geolocation":2,
            "profile.managed_default_content_settings.media_stream":2,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    # chrome_options.add_argument("log-level=3")
    # set user agent
    ua = UserAgent()
    userAgent = ua.random
    chrome_options.add_argument(f'user-agent={userAgent}')
    driver = webdriver.Chrome("../chromedriver", options=chrome_options)

    for i, dt in enumerate(data['url'].items()):
        print(i, ". ", str(dt[1]))
        url = str(dt[1])
        try:
            # open url
            driver.get(url)
            time.sleep(1)

            try:
                headline1 = driver.find_element_by_xpath('.//h1[@class="css-v7vvdw"]')
                article_title = headline1.text
            except:
                article_title = "not found"
                pass
                
            try:
                subcat1 = driver.find_element_by_xpath('.//li[@class="css-1vbldqk"]//a')
                article_subcat = subcat1.text
            except:
                article_subcat = "not found"
                pass

            try:
                desc1 = driver.find_element_by_xpath('.//div[@data-testid="lblPDPDescriptionProduk"]')
                article_description = desc1.text
            except:
                article_description = "not found"
                pass
            
            df['title'] = article_title
            df['sub_category'] = article_subcat
            df['description'] = article_description

            writer.writerow(df.values())

        except Exception as e:
            print("failed scrap the url", e)
            time.sleep(1)
            pass

    # exit the browser
    driver.quit()
    
def ingest_tokopedia_full():
    link_raw = [
        "mie-pasta",
        "sayur-buah",
        "minuman",
        "makanan-sarapan",
        "makanan-beku"
    ]

    for lr in link_raw:
        print(lr)
        # ingest link first
        # ingest throught this function
        ingest_tokopedia_link(lr)
        # preprocessing the links
        # data = pd.read_csv(f"data/link_tokped_{lr}.csv")
        # df_clean = []
        # for dt in data['url'].items():
        #     s = str(dt[1])
        #     if "ta.tokopedia.com" in s:
        #         sa = s[s.find('www.tokopedia.com'):]
        #         sa = sa.replace('%2F','/')
        #         sa = sa[:sa.find('%3F')]
        #         sa = sa[:sa.find('/')]
        #         sa = "https://" + sa
        #     else:
        #         sa = s
        #     df_clean.append(sa)
        
        # df = pd.DataFrame()
        # df['url'] = df_clean
        # df.to_csv(f"data/link_outlet_tokped_{lr}.csv", index=False)
        # replace the files (split to several files, if the process takes long)
        # df2 = df.copy()
        # df3 = df.copy()
        # df = df[:500]
        # df2 = df2[500:1000]
        # df3 = df3[1000:]
        # # set the parameter
        # ct1 = lr+"_1"
        # ct2 = lr+"_2"
        # ct3 = lr+"_3"
        # df.to_csv(f"data/link_tokped_{ct1}.csv", index=False)
        # df2.to_csv(f"data/link_tokped_{ct2}.csv", index=False)
        # df3.to_csv(f"data/link_tokped_{ct3}.csv", index=False)
        # del df, df2, df3

        # ingest description then
        # ingest_tokopedia_desc(ct1)
        # ingest_tokopedia_desc(ct2)
        # ingest_tokopedia_desc(ct3)

    
def ingest_bukalapak_full():
    category = 'bumbu'
    url = f'https://www.bukalapak.com/c/food/{category}'

    # call open browser function
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.headless = True
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--incognito')
    chrome_options.add_argument("log-level=3")
    # set user agent
    ua = UserAgent()
    userAgent = ua.random
    chrome_options.add_argument(f'user-agent={userAgent}')
    driver = webdriver.Chrome("../chromedriver", options=chrome_options)
    # open url
    driver.get(url)

    # set csv
    # today = date.today()
    csv_file = open(f'data/bukalapak/bl_{category}.csv', 'w', encoding='utf-8') 
    writer = csv.writer(csv_file)

    total_all = 0
    df = {}
    total_product = 0
    for i in range(1, 31):
        print(f"iterasi ke {i}")
        driver.execute_script("window.scrollTo(0, 1000)")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0)")
        time.sleep(1)
        
        try:
            linklists = None
            linklists = driver.find_elements_by_xpath('.//div[@class="bl-product-card__description-name"]//a[@href]')
            linklists_total = len(linklists)
            print(linklists_total)
            for k in range(0, linklists_total):
                time.sleep(1)
                try:                        
                    linklist = None
                    linklist = driver.find_elements_by_xpath('.//div[@class="bl-product-card__description-name"]//a[@href]')
                    url_w = linklist[k].get_attribute('href')
                    title1 = linklist[k].text
                    # print(title1)
                    print(url_w)

                    # time.sleep(2)
                    linklist[k].click()
                    time.sleep(1)
                    
                    # scraping description
                    try:
                        desc = driver.find_element_by_xpath('.//div[@class="c-information__description-txt"]')
                        desc1 = desc.text
                    except:
                        try:
                            desc1 = ''
                            desc = driver.find_elements_by_xpath('.//div[@class="c-information__description-txt"]//p')
                            for ds in desc:
                                desc1 += ds.text
                        except (NoSuchElementException, StaleElementReferenceException) as e:
                            desc1 = ''
                            pass

                    try:
                        subcat = driver.find_element_by_xpath('.//table[@class="c-information__table"]//a[@href]')
                        subcat1 = subcat.text
                    except (NoSuchElementException, StaleElementReferenceException) as e:
                        subcat1 = ''
                        pass
                    
                    df['title'] = title1
                    df['description'] = desc1
                    df['sub_category'] = subcat1
                    df['category'] = category
                    writer.writerow(df.values())

                    driver.back()

                    if k>=14:
                        driver.execute_script("window.scrollTo(0, 1500)")
                        time.sleep(2)
                        pass

                except Exception as e:
                    print("failed scrap in product", e)
                    time.sleep(1)
                    pass
                # time.sleep(2)
                # df['link'] = url_w
                # writer.writerow(df.values())


            total_product = total_product+linklists_total

        except Exception as e:
            print("failed scrap in page", e)
            time.sleep(1)
            pass

        j = i+1
        url2 = f"https://www.bukalapak.com/c/food/{category}?page={j}"
        driver.get(url2)

    print("total halaman {} dan total item {}".format(total_all+1, total_product))
    driver.quit()

def ingest_shopee():
    category = 'Roti-Kue-cat.157.18449'
    cat = category.split('-')
    category_name = str(cat[0])+"_"+str(cat[1])
    url = f'https://shopee.co.id/{category}'

    # call open browser function
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.headless = True
    # chrome_options.add_argument(--headless)
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--incognito')
    chrome_options.add_argument("log-level=3")
    # set user agent
    ua = UserAgent()
    userAgent = ua.random
    chrome_options.add_argument(f'user-agent={userAgent}')
    driver = webdriver.Chrome('../chromedriver', options=chrome_options)
    # driver = webdriver.Chrome('../chromedriver_mac', options=chrome_options)
    # open url
    driver.get(url)

    # set csv
    # today = date.today()
    csv_file = open(f'data/detail/shopee_{category_name}.csv', 'w', encoding='utf-8') 
    writer = csv.writer(csv_file)

    total_all = 0
    df = {}
    total_product = 0
    for i in range(0, 51):
        print(f"iterasi ke {i}")
        time.sleep(2)
        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        driver.execute_script("window.scrollTo(0, 2800)")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 1750)")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0)")
        time.sleep(2)
        
        try:
            linklists = None
            linklists = driver.find_elements_by_xpath('.//div[@class="col-xs-2-4 shopee-search-item-result__item"]//a[@href]')
            linklists_total = len(linklists)
            print(linklists_total)
            time.sleep(1)
            for k in range(0, linklists_total):
                try:                        
                    linklist = None
                    linklist = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH,'.//div[@class="col-xs-2-4 shopee-search-item-result__item"]//a[@href]')))
                    url_w = linklist[k].get_attribute('href')
                    print(str(k+1)+". "+url_w)

                    # time.sleep(2)
                    linklist[k].click()
                    time.sleep(1)
                    
                    # scraping description
                    try:
                        title = driver.find_element_by_xpath('//div[@class="attM6y"]//span')
                        title1 = title.text
                    except (NoSuchElementException, StaleElementReferenceException) as e:
                        title1 = ''
                        pass

                    try:
                        desc = driver.find_element_by_xpath('.//div[@class="_3yZnxJ"]//span')
                        desc1 = desc.text
                    except (NoSuchElementException, StaleElementReferenceException) as e:
                        desc1 = ''
                        pass

                    try:
                        subcat = driver.find_elements_by_xpath('.//div[@class="flex items-center _1J-ojb"]//a[@href]')
                        subcat1 = subcat[-1].text
                    except (NoSuchElementException, StaleElementReferenceException) as e:
                        subcat1 = ''
                        pass
                    
                    df['title'] = title1
                    df['description'] = desc1
                    df['sub_category'] = subcat1
                    df['category'] = category_name
                    writer.writerow(df.values())

                    driver.back()

                    # if k>=29:
                    #     driver.execute_script("window.scrollTo(0, 3000)")
                    #     time.sleep(2)
                    #     pass
                    # elif k>=24 and k<39:
                    #     driver.execute_script("window.scrollTo(0, 2400)")
                    #     time.sleep(2)
                    #     # pass
                    # elif k>=39:
                    #     driver.execute_script("window.scrollTo(0, 2700)")
                    #     time.sleep(2)
                    #     # pass

                except Exception as e:
                    print("failed scrap in product", e)
                    time.sleep(1)
                    pass

            total_product = total_product+linklists_total

        except Exception as e:
            print("failed scrap in page", e)
            time.sleep(1)
            pass

        j = i+1
        url2 = f"https://shopee.co.id/{category}?page={j}"
        driver.get(url2)

    print("total halaman {} dan total item {}".format(total_all+1, total_product))
    driver.quit()

def ingest_shopee_link(category):
    cat = category.split('-')
    # category_name = str(cat[0])+"_"+str(cat[1])
    category_name = str(cat[0])
    url = f'https://shopee.co.id/{category}'

    # call open browser function
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    # chrome_options.headless = True
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--incognito')
    chrome_options.add_argument("log-level=3")
    # set user agent
    # ua = UserAgent()
    # userAgent = ua.random
    # chrome_options.add_argument(f'user-agent={userAgent}')
    driver = webdriver.Chrome('../chromedriver', options=chrome_options)
    # open url
    driver.get(url)

    # set csv
    # today = date.today()
    csv_file = open(f'data/link_shopee_{category_name}.csv', 'w', encoding='utf-8') 
    writer = csv.writer(csv_file)

    total_all = 0
    df = {}
    total_product = 0
    for i in range(0, 100):
        print(f"iterasi ke {i}")
        time.sleep(3)
        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        driver.execute_script("window.scrollTo(0, 3000)")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 1750)")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0)")
        time.sleep(1)
        
        try:
            linklists = None
            linklists = driver.find_elements_by_xpath('.//div[@class="col-xs-2-4 shopee-search-item-result__item"]//a[@href]')
            linklists_total = len(linklists)
            print(linklists_total)
            for k in range(0, linklists_total):
                time.sleep(1)
                try:                        
                    # linklist = None
                    # linklist = driver.find_elements_by_xpath('.//div[@class="col-xs-2-4 shopee-search-item-result__item"]//a[@href]')
                    linklist = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, './/div[@class="col-xs-2-4 shopee-search-item-result__item"]//a[@href]')))
                    url_w = linklist[k].get_attribute('href')
                    print(str(k+1)+"."+url_w)
                    df['link'] = url_w
                    writer.writerow(df.values())

                    total_product = total_product+k
                except Exception as e:
                    print("failed to get link", e)
                    time.sleep(1)
                    pass
        except Exception as e:
            print("failed to next page", e)
            time.sleep(1)
            pass

        j = i+1
        url2 = f"https://shopee.co.id/{category}?page={j}"
        driver.get(url2)

    # print("total halaman {} dan total item {}".format(total_all+1, total_product))
    driver.quit()

def ingest_shopee_desc(category):
    # category = 'Makanan-Instan-cat.157.12561'
    cat = category.split('-')
    category_name = str(cat[0])+"_"+str(cat[1])
    # url = f'https://shopee.co.id/{category}'

    # call open browser function
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    # chrome_options.headless = True
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--incognito')
    # chrome_options.add_argument("log-level=3")
    # prefs = {"profile.managed_default_content_settings.images":2,
    #         "profile.default_content_setting_values.notifications":2,
    #         "profile.managed_default_content_settings.stylesheets":2,
    #         "profile.managed_default_content_settings.cookies":2,
    #         "profile.managed_default_content_settings.javascript":1,
    #         "profile.managed_default_content_settings.plugins":1,
    #         "profile.managed_default_content_settings.popups":2,
    #         "profile.managed_default_content_settings.geolocation":2,
    #         "profile.managed_default_content_settings.media_stream":2,
    # }
    # chrome_options.add_experimental_option("prefs", prefs)
    # set user agent
    ua = UserAgent()
    userAgent = ua.random
    chrome_options.add_argument(f'user-agent={userAgent}')
    driver = webdriver.Chrome('../chromedriver', options=chrome_options)
    # open url
    # driver.get(url)

    # open data from link csv
    data = pd.read_csv(f"data/link_shopee_{category_name}.csv", names=["url"])

    # set csv
    # today = date.today()
    csv_file = open(f'data/shopee/shopee_{category_name}.csv', 'w', encoding='utf-8') 
    writer = csv.writer(csv_file)

    total_all = 0
    df = {}
    total_product = 0
    for i, url_w in enumerate(data['url'].items()):
        time.sleep(2)
        try:                     
            driver.get(str(url_w[1]))

            # scraping description
            try:
                time.sleep(1)
                title = driver.find_element_by_xpath('//div[@class="attM6y"]//span')
                title1 = title.text
            except (NoSuchElementException, StaleElementReferenceException) as e:
                title1 = ''
                pass

            try:
                time.sleep(1)
                desc = driver.find_element_by_xpath('.//div[@class="_3yZnxJ"]//span')
                desc1 = desc.text
            except (NoSuchElementException, StaleElementReferenceException) as e:
                desc1 = ''
                pass

            try:
                time.sleep(1)
                subcat = driver.find_elements_by_xpath('.//div[@class="flex items-center _1J-ojb"]//a[@href]')
                subcat1 = subcat[-1].text
            except (NoSuchElementException, StaleElementReferenceException) as e:
                subcat1 = ''
                pass
            
            print(str(i+1)+"."+title1)
            df['title'] = title1
            df['description'] = desc1
            df['sub_category'] = subcat1
            df['category'] = category_name
            # print(df)
            writer.writerow(df.values())

            # total_product = total_product+k
        except Exception as e:
            print("failed to get data description", e)
            time.sleep(1)
            pass

    # print("total halaman {} dan total item {}".format(total_all+1, total_product))
    driver.quit()

def ingest_shopee_full():
    link_raw = [
        # 'Bahan-Pokok-cat.157.14560',
        # 'Roti-Kue-cat.157.18449',
        # 'Cokelat-Permen-cat.157.14582',
        'Susu-Olahan-cat.157.14574',
        # 'Makanan-Minuman-Lainnya-cat.157.347'
        # 'Minuman-cat.157.1445',
    ]

    for lr in link_raw:
        print(lr)
        # ingest_shopee_link(lr)
        ingest_shopee_desc(lr)