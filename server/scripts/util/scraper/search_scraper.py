from browser import get_chrome_driver

import re

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

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
        print("Inside of try")

        search = driver.find_element("name", "q")
        search.send_keys(query)
        search.send_keys(Keys.RETURN)

        wait = WebDriverWait(driver, 10)
        result_element = wait.until(EC.presence_of_element_located((By.ID, "result-stats")))
        html = result_element.get_attribute('outerHTML')

        match = re.search(r'About\s+([\d,]+)\s+results', html)

        return (int(match.group(1).replace(',', '')), -1)[match]

    except Exception as e:
        print("Inside of catch")



def scrape_urls_from_query(query):
    print("Inside of scrape urls from query")