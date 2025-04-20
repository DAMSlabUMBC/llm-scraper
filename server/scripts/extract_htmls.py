import os
import logging
import threading
from queue import Queue

from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import requests

from util.scraper.proxy import (
    download_proxy,
    load_proxy,
    find_working_proxy,
    local_access,
)
from util.scraper.browser import get_chrome_driver

# -----------------------------------------------------------------------------
# Logging configuration
# -----------------------------------------------------------------------------
logging.basicConfig(
    filename='html_extractor.log',
    filemode='a',
    level=logging.INFO,
)

# -----------------------------------------------------------------------------
# Constants & globals
# -----------------------------------------------------------------------------
URLS_FILE       = "Amazon_product_urls.txt"
FOLDER_NAME     = "amazon_htmls"
GROUP           = "amazon"

working_proxy   = None
thread_lock     = threading.Lock()
PROXIES         = []
fake_useragent  = UserAgent()
failed_proxies  = set()


def extract_html(url: str, html_number: int) -> None:
    """
    Extracts the HTML of the given URL (using local access or a proxy),
    then writes it out to a file named f"{GROUP}{html_number}.html" in FOLDER_NAME.
    """
    file_name = f"{GROUP}{html_number}.html"
    global working_proxy

    print(f"[🔍] Scraping URL: {url}")

    # Try direct (local) access first
    if local_access(url):
        print("[✅] Local access successful.")
    else:
        # Fallback to proxies
        download_proxy()
        load_proxy()
        working_proxy = find_working_proxy()
        if working_proxy is None:
            load_proxy()
            working_proxy = find_working_proxy()
        if working_proxy is None:
            print("[❌] No working proxy found.")
            return
        print(f"[🛰️] Using working proxy: {working_proxy}")

    # Selenium WebDriver setup
    driver = get_chrome_driver(headless=True, use_proxy=working_proxy)
    try:
        driver.get(url)
        html = driver.page_source

        # Ensure the output folder exists
        os.makedirs(FOLDER_NAME, exist_ok=True)
        file_path = os.path.join(FOLDER_NAME, file_name)

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(html)

    except Exception as e:
        print(f"[⚠️] Page crash detected for {file_name}, skipping...")
        print(f"Error: {e}")
        logging.error(f"Error extracting contents from {GROUP} link #{html_number}: {e}")
    finally:
        driver.quit()


if __name__ == '__main__':
    # Read all product URLs
    with open(URLS_FILE, "r") as f:
        urls = [u.strip() for u in f if u.strip()]

    # Scrape each URL in turn
    for i in tqdm(range(len(urls)), desc="Extracting HTML"):
        extract_html(urls[i], i)
