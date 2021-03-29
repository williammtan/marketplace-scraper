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
            products = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, './/div[@class="css-bk6tzz e1nlzfl3"]//a[@href]')))
            time.sleep(2)
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

def ingest_tokopedia_desc():
    category = "bumbu_6"
    data = pd.read_csv(f"link_tokped_{category}.csv")

    # set csv
    today = date.today()
    csv_file = open(f'tokped_{category}.csv', 'w', encoding='utf-8') 
    writer = csv.writer(csv_file)

    df = {}
    for i, dt in enumerate(data['url'].items()):
        print(i, ". ", str(dt[1]))
        url = str(dt[1])
        try:
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
            # set user agent
            ua = UserAgent()
            userAgent = ua.random
            chrome_options.add_argument(f'user-agent={userAgent}')
            driver = webdriver.Chrome("../chromedriver", options=chrome_options)
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
                subcat1 = driver.find_element_by_xpath('.//li[@class="css-r0v3c0"]//a')
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

        except Exception as e:
            print("failed scrap the url", e)
            time.sleep(1)
            pass

        df['title'] = article_title
        df['sub_category'] = article_subcat
        df['description'] = article_description

        writer.writerow(df.values())

    # exit the browser
    driver.quit()
    
def ingest_tokopedia():
    link_raw = [
        "makanan-beku",
        "makanan-jadi",
        "makanan-ringan",
        "makanan-kaleng",
        "makanan-kering",
        "makanan-sarapan"
    ]

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

    for lr in link_raw:
        print(lr)
        # ingest throught this function
        ingest_tokopedia_link(lr)
        # preprocessing the links
        data = pd.read_csv(f"data/link_tokped_{category}.csv")
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
        # replace the files (split to two file if its the process takes long)
        df.to_csv(f"data/link_tokped_{category}.csv", index=False)
    
