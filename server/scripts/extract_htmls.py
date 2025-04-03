from tqdm import tqdm
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import requests
from queue import Queue
import threading
from util.scraper.proxy import download_proxy, load_proxy, find_working_proxy, local_access
from util.scraper.browser import get_chrome_driver
import logging

logging.basicConfig(
    filename='html_extractor.log',  # Log file name
    filemode = "a",
    level=logging.INFO,  # Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
)

URLS_FILE = "Amazon_product_urls.txt"
FOLDER_NAME = "amazon_htmls"
GROUP = "amazon"

working_proxy = None
thread_lock = threading.Lock()
PROXIES = []
fake_useragent = UserAgent()
failed_proxies = set()

def extract_html(url, html_number):
    file_name = f"{GROUP}{html_number}.html"
    global working_proxy
    print(f"[🔍] Scraping url:", url)
    
    if local_access(url):
        print("[✅] Local access successful.")
    else:
        download_proxy()
        load_proxy()
        working_proxy = find_working_proxy()
        if working_proxy is None:
            load_proxy()
            working_proxy = find_working_proxy()
        if working_proxy is None:
            print("[❌] No working proxy found.")
            return None
        
        print(f"[🛰️] Using working proxy: {working_proxy}")

    # Selenium WebDriver Configuration
    driver = get_chrome_driver(headless=True, use_proxy=working_proxy)

    try:
        driver.get(url)
        html = driver.page_source

        file_path = os.path.join(FOLDER_NAME, file_name)
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(html)
    except Exception as e:
        print(f"Page crash detected for {file_name}, skipping...")
        print(f"Error: {e}")
        logging.error(f"Error extracting contents from {GROUP} link {html_number}")
            
    

if __name__ == '__main__':
    urls = []
    # gets the product urls from the txt file
    with open(URLS_FILE, "r") as f:
        urls = [url.strip() for url in f.readlines()]

    for i in tqdm(range(len(urls))):
        extract_html(urls[i], i)
        
