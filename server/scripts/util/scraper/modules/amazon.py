from util.scraper.browser import get_chrome_driver
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm
import time
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import cloudscraper
import requests
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '/home/gsantos2/gia_ada/llm-scraper/server/scripts/util/scraper'))

from browser import get_chrome_driver


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

        # starts the chrome driver
        driver = get_chrome_driver()

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
                try:
                    req = self.scraper.get(url)
                    soup = BeautifulSoup(req.content, 'html.parser')
                    nextPage = soup.find('a', {"class": "s-pagination-item s-pagination-next s-pagination-button s-pagination-button-accessibility s-pagination-separator"})
                    # s-pagination-item s-pagination-next s-pagination-button s-pagination-button-accessibility s-pagination-separator
                    url = self.home + nextPage["href"]
                    driver.get(url)

                    time.sleep(2) # wait for page to load
                    print("next page")

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
    
    def parseProducts(self, soup):
        """
        parses a product from Amazon

        Parameters
        soup: html code to parse

        Return
        self.process_record(product): dictionary of product information
        """
        name = soup.find("span", {"class": "a-size-large product-title-word-break"})
        if name != None:
            print("FOUND NAME")
            name = name.get_text(strip=True)
        
        if name == None:
            name = soup.find("div", {"id": "title_feature_div"})
            if name != None:
                print("FOUND NAME")
                name = name.get_text(strip=True)
                
        if name == None:
            name = soup.find("span", {"id": "title"})
            if name != None:
                print("FOUND NAME")
                name = name.get_text(strip=True)
                
                
            
        #class="a-normal a-spacing-micro"
        
        manufacturer = soup.find("div", {"class": "a-section a-spacing-small a-spacing-top-small"})
        if manufacturer != None:
            manufacturer = soup.find("table", {"class": "a-normal a-spacing-micro"})
            if manufacturer != None:
                manufacturer = manufacturer.find("tr", {"class": "a-spacing-small po-brand"})
                if manufacturer != None:
                    manufacturer = manufacturer.find("td", {"class": "a-span9"})
                    if manufacturer != None:
                        manufacturer = manufacturer.find("span", {"class": "a-size-base po-break-word"})
                        if manufacturer != None:
                            print("FOUND MANUFACTURER")
                            manufacturer = manufacturer.get_text(strip=True)
        if manufacturer == None:
            manufacturer = soup.find("a", {"class": "a-color-base a-link-normal a-text-bold"})
            if manufacturer != None:
                print("FOUND MANUFACTURER")
                manufacturer = manufacturer.get_text(strip=True)

        details_elements = soup.select('.a-unordered-list.a-vertical.a-spacing-mini')
        details = ' | '.join([elem.get_text(strip=True) for elem in details_elements])
        
        if details == "":
            details_elements = soup.find('div', {'id': 'feature-bullets'})

            # Extract all bullet points
            if details_elements:
                details = ' | '.join([li.get_text(strip=True) for li in details_elements.find_all('li')])

        # finds the url to the product
        url = soup.find("link", {"rel": "canonical"})
        if url != None:
            url = url["href"]
        else:
            url = ""
        # turns it into a product of the necessary format
        product = {
            "name": name,
            "manufacturer": manufacturer,
            "details": details
        }
        
        return str(product), url