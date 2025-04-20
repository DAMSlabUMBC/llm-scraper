from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException
import chromedriver_autoinstaller
import time
import argparse
import json
import os
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
from urllib.parse import urljoin
#from scraping import local_access, download_proxy, load_proxies, find_working_proxy

CONFIGS_FOLDER = "config_files"
working_proxy = None

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Connection": "keep-alive"
}

def click_next(driver, configs):

    try:
        print("🔍 Looking for next button with selector:", configs["next"])

        # Wait up to 10s for the next button to appear and be clickable
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, configs["next"]))
        )

        # Scroll into view in case it's offscreen
        driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
        time.sleep(0.5)

        # Try to click it directly
        next_href = next_button.get_attribute("href")
        if not next_href:
            print("⚠️ Next button found but no href.")
            next_button.click()
            time.sleep(2)
        else:
            next_href = urljoin(configs["home_url"], next_href)
            print("👉 Navigating to:", next_href)
            driver.get(next_href)
            time.sleep(2)  # Let JS render

        return BeautifulSoup(driver.page_source, "html.parser")

    except TimeoutException:
        print("❌ Timeout: Next button not found.")
    except NoSuchElementException:
        print("❌ Element not found: Are you sure the selector is correct?")
    except Exception as e:
        print("❌ Selenium error navigating to next page:", e)

    return None

if __name__ == "__main__":
    product_urls = set()

    # initializes argument parser
    parser = argparse.ArgumentParser(description="Process an input file and save output.")

    parser.add_argument("--config_file", required=True, help="json with configurations to a specific site")

    # parses the arguments
    args = parser.parse_args()

    # sets the input and output files
    config_file = args.config_file

    with open(os.path.join(CONFIGS_FOLDER, config_file), 'r') as f:
        configs = json.load(f)

    print(configs)
    print(f"PRODUCT URL TAGS {configs["product_urls"]}")
    #exit()

    # gets all the search queries
    with open("search_queries.txt", "r") as f:
        search_queries = f.readlines()

    # Automatically install matching chromedriver
    chromedriver_autoinstaller.install()

    options = Options()
    options.headless = True
    fake_useragent = UserAgent()
    options.add_argument(f'user-agent={fake_useragent.random}')
    
    #options.add_argument("--headless")  # Run headless
    options.add_argument("--no-sandbox")  # Necessary for some restricted environments
    options.add_argument("--disable-dev-shm-usage")  # Overcome resource limitations


    # Set up the Chrome browser
    driver = webdriver.Chrome(options=options)

    # Open the website
    driver.get(configs["home_url"])

    wait = WebDriverWait(driver, 30)

    # finds the search box
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, configs["search_bar"])))
        search_box = driver.find_element(By.CSS_SELECTOR, configs["search_bar"])
    except Exception as e:
        print("❌ Could not find search bar:", e)
        driver.save_screenshot("error_screenshot.png")
        with open("error_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        exit()

    #print(f"{configs["search_bar"]["elem"]}#{configs["search_bar"]["id"]}.{".".join(configs["search_bar"]["class"].split())}")
    #exit()
    # Optional: wait a bit for elements to load
    search_queries = search_queries[1:]

    with open(configs["temp_urls"], "a") as f:

        for search in tqdm(search_queries):
            

            #print(f"{configs["search_bar"]["elem"]}#{".".join(configs["search_bar"]["class"].split())}")

            try:
                # Attempt to clear the search box
                search_box.clear()
            except StaleElementReferenceException:

                # Re-locate the search box if it's stale
                search_box = driver.find_element(By.CSS_SELECTOR, f"{configs["search_bar"]}")
                search_box.clear()

            # Type the search query
            search_box.send_keys(search.strip())

            # Submit the search (press ENTER)
            search_box.send_keys(Keys.RETURN)

            html = driver.page_source

            # Parse the HTML using BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")

            # Find all elements matching the selector
            # Note: BeautifulSoup doesn't support full CSS selectors the way Selenium does (like :nth-child),
            # so you may need to tweak the selector to use classes, ids, tags, etc.
            product_elements = soup.select(configs["product_urls"])

            # Extract the href from each product link
            for product in product_elements:
                href = product.get("href")
                if href:
                    # If it's a relative URL, you might want to prefix with base URL:
                    if href.startswith("/"):
                        href = configs["home_url"].rstrip("/") + href
                    f.write(href + "\n")

            # # Optional: wait to view the result
            # time.sleep(10)

            # # obtains the product links
            # products = driver.find_elements(By.CSS_SELECTOR, f"{configs["product_urls"]}")
            while soup:
                # Parse the HTML using BeautifulSoup
                #soup = BeautifulSoup(html, "html.parser")

                # Find all elements matching the selector
                # Note: BeautifulSoup doesn't support full CSS selectors the way Selenium does (like :nth-child),
                # so you may need to tweak the selector to use classes, ids, tags, etc.
                product_elements = soup.select(configs["product_urls"])

                # Extract the href from each product link
                for product in product_elements:
                    href = product.get("href")
                    if href:
                        # If it's a relative URL, you might want to prefix with base URL:
                        if href.startswith("/"):
                            href = configs["home_url"].rstrip("/") + href
                        f.write(href + "\n")

                soup = click_next(driver, configs)

                # waits to view the results
                time.sleep(10)

            
            # reloads the page to the home page
            driver.get(configs["home_url"])
            time.sleep(2)

            search_bar = driver.find_element(By.CSS_SELECTOR, configs["search_bar"])
            

        # Close the browser
        driver.quit()

    with open(configs["temp_urls"], "r") as f:
        product_urls = f.readlines()

    with open(configs["official_urls"], "r") as f:
        product_urls.extend(f.readlines())

    product_urls = set(product_urls)

    with open(configs["official_urls"], "w") as f:
        for url in product_urls:
            f.write(url)