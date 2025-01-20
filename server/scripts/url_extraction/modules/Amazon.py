#from lab_scraper.modules.module import Module
#from modules.module import Module
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm
import time
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import cloudscraper
import requests



class Amazon():
    """
    defines the module for Amazon as well as it's specific parser
    """

    def __init__(self):
        super().__init__()
        self.name = "Amazon"
        self.home = "https://www.amazon.com/s?k="
        self.scraper = cloudscraper.create_scraper(delay=10,   browser={'custom': 'ScraperBot/1.0',})
        

    def fetchURLs(self, search_urls):
        """
        fetches all product URLs from Amazon

        Parameters
        search_urls: list of search urls to parse product urls from

        Return
        product_urls: a list of product URLs
        """

        # configures chrome driver options
        chrome_options = Options()
        chrome_options.binary_location = "/usr/bin/google-chrome"  # Replace with the actual path to google-chrome
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")  # Prevent sandboxing issues
        chrome_options.add_argument("--disable-dev-shm-usage")  # Fix shared memory issues
        chrome_options.add_argument("--disable-gpu")  # Useful for headless mode
        chrome_options.add_argument("--remote-debugging-port=9222")  # Avoid conflicts
        chrome_options.add_argument("--verbose")

        # starts the chrome driver
        driver = webdriver.Chrome(service=Service(), options=chrome_options)

        product_urls = []
        # iterates through each url after search
        for url in tqdm(search_urls):

            #stop = False

            # to remove the newline character
            url = url.rstrip()

            driver.get(url)
            time.sleep(2) # wait for page to load

            # bypasses humna-robot verification
            #blocked = self.driver.find_element(By.CSS_SELECTOR, 'a.heading heading-d sign-in-widget')
            

            # gets the links of each product on the web page
            product_links = set(a.get_attribute('href') for a in driver.find_elements(By.CSS_SELECTOR, 'a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal'))
            product_links = list(product_links)

            product_urls.extend(product_links)

            stop = False
            #print("searching for next page")
            while not stop:
                print("next page")
                try:
                    req = self.scraper.get(url)
                    soup = BeautifulSoup(req.content, 'html.parser')
                    nextPage = soup.find('a', {"class": "s-pagination-item s-pagination-next s-pagination-button s-pagination-button-accessibility s-pagination-separator"})
                    # class="s-pagination-item s-pagination-next s-pagination-button s-pagination-button-accessibility s-pagination-separator"
                    #print("nextPage", nextPage)
                    url = self.home + nextPage["href"]
                    driver.get(url)

                    time.sleep(2) # wait for page to load

                    # gets the links of each product on the web page
                    product_links = set(a.get_attribute('href') for a in driver.find_elements(By.CSS_SELECTOR, 'a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal'))
                    product_links = list(product_links)

                    product_urls.extend(product_links)

                except:
                    print("no next page")
                    stop = True
                
        # done with driver
        driver.close()
        
        return product_urls