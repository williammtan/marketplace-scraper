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

def ingest_tokopedia_link(category):
    # category = 'kue'
    url = f'https://www.tokopedia.com/p/makanan-minuman/{category}'

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

    total_all = 0
    url_w = []
    for i in range(0, 25):
        print(f"iterasi ke {i}")
        # time.sleep(10)
        j = i+2
        url2 = f"https://www.tokopedia.com/p/makanan-minuman/{category}?page={j}"
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
                    url_w.append(linklist[k].get_attribute('href'))
                    # time.sleep(2)

                except Exception as e:
                    print("failed scrap", e)
                    time.sleep(1)
                    pass

            time.sleep(2)
            driver.get(url2)
        except Exception as e:
            print("failed to next page", e)
            time.sleep(1)
            pass

    df = pd.DataFrame()
    df['url'] = url_w
    print(len(df.index))
    df.to_csv(f'data/link_tokped_{category}.csv', index=False)

    print(total_all)
    driver.quit()

def ingest_tokopedia_desc(category):
    # category = "teh_2"
    data = pd.read_csv(f"data/link_tokped_{category}.csv")

    # set csv
    today = date.today()
    csv_file = open(f'data/detail/tokped_{category}.csv', 'w', encoding='utf-8') 
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
    
def ingest_tokopedia():
    link_raw = [
        "kopi",
        "teh"
    ]

    for lr in link_raw:
        print(lr)
        # ingest link first
        # ingest throught this function
        ingest_tokopedia_link(lr)
        # preprocessing the links
        data = pd.read_csv(f"data/link_tokped_{lr}.csv")
        df_clean = []
        for dt in data['url'].items():
            s = str(dt[1])
            if "ta.tokopedia.com" in s:
                sa = s[s.find('www.tokopedia.com'):]
                sa = sa.replace('%2F','/')
                sa = sa[:sa.find('%3F')]
                sa = "https://" + sa
            else:
                sa = s
            df_clean.append(sa)
        
        df = pd.DataFrame()
        df['url'] = df_clean
        # replace the files (split to several files, if the process takes long)
        df2 = df.copy()
        df3 = df.copy()
        df = df[:500]
        df2 = df2[500:1000]
        df3 = df3[1000:]
        # set the parameter
        ct1 = lr+"_1"
        ct2 = lr+"_2"
        ct3 = lr+"_3"
        df.to_csv(f"data/link_tokped_{ct1}.csv", index=False)
        df2.to_csv(f"data/link_tokped_{ct2}.csv", index=False)
        df3.to_csv(f"data/link_tokped_{ct3}.csv", index=False)
        del df, df2, df3

        # ingest description then
        ingest_tokopedia_desc(ct1)
        ingest_tokopedia_desc(ct2)
        ingest_tokopedia_desc(ct3)

    
def ingest_bl_link():
    category = 'minuman'
    url = f'https://www.bukalapak.com/c/food/{category}?page=5'

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
    csv_file = open(f'data/link_bl_{category}_2.csv', 'w', encoding='utf-8') 
    writer = csv.writer(csv_file)

    total_all = 0
    df = {}
    total_product = 0
    for i in range(5, 30):
        print(f"iterasi ke {i}")
        driver.execute_script("window.scrollTo(0, 1500)")
        driver.execute_script("window.scrollTo(0, 0)")
        time.sleep(2)
        
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