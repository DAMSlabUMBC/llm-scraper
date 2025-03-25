from browser import get_chrome_driver

import re
import time

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from urllib.parse import urlparse

def scrape_search_result_count_from_query(query):
    """
    Uses selenium to search for the query and grabs the 'result-stats' id tag that
    Google uses to provide an approximate number of search results (e.g. "About 1,000,000 results")

    Args:
        query (string): Google search  

    Returns:
        search result count (int): If there is approximate search result found return it, else -1
    """

    driver = get_chrome_driver()
    driver.get("https://www.google.com")

    try:
        search = driver.find_element("name", "q")
        search.send_keys(query)
        search.send_keys(Keys.RETURN)

        wait = WebDriverWait(driver, 10)
        result_element = wait.until(EC.presence_of_element_located((By.ID, "result-stats")))
        html = result_element.get_attribute('outerHTML')

        match = re.search(r'About\s+([\d,]+)\s+results', html)

        return (int(match.group(1).replace(',', '')), -1)[match]

    except Exception as e:
        print("Error Finding id tag 'result-stats': ", e)
        return -1
    finally:
        driver.quit()

def scrape_urls_from_query(query, max_urls=5, excluded_domains=None, excluded_paths=None):
    """
    Uses selenium to search for the query and grabs the top 5 results

    Args:
        query (string): Google search
        max_urls (int): Maximum number of result URLs to return, default is 5.
        excluded_domains (dictionary): Urls to ignore, default is none
        excluded_paths (dictionary): Paths to ignore, default is none

    Returns:
        list[str]: A list of filtered result URLs (excluding specified domans and paths).
    """

    result = []
    seen = set()

    driver = get_chrome_driver()
    driver.get('https://www.google.com')

    try:    
        search = driver.find_element("name", "q")
        search.send_keys(query)
        search.send_keys(Keys.RETURN)

        wait = WebDriverWait(driver, 10)

        anchor_elements = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))

        count = 0

        for element in anchor_elements:
            if count >= max_urls:
                break

            href = element.get_attribute("href")

            if not href:
                continue

            parsed = urlparse(href)
            domain = parsed.netloc 
            path = parsed.path

            if domain not in excluded_domains and path not in excluded_domains:
                continue
        
            if href not in seen:
                print(href)
                result.append(href)
                seen.add(href)
                count += 1
    
    except Exception as e:
        print("Error fetching URLs from query:", e)
    finally:
        driver.quit()
        return result
