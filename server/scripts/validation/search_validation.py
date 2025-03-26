import requests
import os
import ast
from dotenv import load_dotenv
import torch
from sentence_transformers import SentenceTransformer, util

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import threading
from urllib.parse import urlparse
import time
import re

# Load environment variables
load_dotenv()


def get_triplets(filename):

    """
    Function to grab the triplets from the file
    """
    with open(filename, "r", encoding="utf-8") as file:
        try:
            triplets = ast.literal_eval(file.read())
            return triplets
        except (SyntaxError, ValueError) as e:
            print(f"Error parsing file: {e}")
            return []

def format_triplet(triplet):
    """
    Converts a structured triplet into a human-readable query.

    Example:
    ('device', 'Govee Smart LED Light Bars') performs ('process', 'location tracking')
    → "Govee Smart LED Light Bars performs location tracking"
    """
    subject, predicate, obj = triplet
    if predicate == 'developedBy':
        predicate = 'is developed by'
        return f"{subject[1]} {predicate} {obj[1]}"
    elif predicate == 'manufacturedBy':
        predicate = 'manufactures'
        return f"{obj[1]} {predicate} {subject[1]}"
    elif predicate == 'compatibleWith':
        predicate = 'is compatible with'
        return f"{subject[1]} {predicate} {obj[1]}" 
    elif predicate == 'hasSensor':
        predicate = 'has'
        return f"{subject[1]} {predicate} {obj[1]}" 
    elif predicate == 'accessSensor':
        predicate = "can access"
        return f"{subject[1]} {predicate} {obj[1]}" 
    elif predicate == 'requiresSensor':
        return f"{subject[1]} {predicate} {obj[1]}" 
    elif predicate == 'performs':
        return f"{subject[1]} {predicate} {obj[1]}" 
    elif predicate == 'hasPolicy':
        predicate = 'has policy'
        return f"{subject[1]} {predicate} {obj[1]}" 
    elif predicate == 'statesInPolicy':
        predicate = 'states that there is'
        return f"{obj[1]} {predicate} {subject[1]}" 
    elif predicate == 'captures':
        return f"{subject[1]} {predicate} {obj[1]}" 
    elif predicate == 'canInfer':
        predicate = 'can infer'
        return f"{subject[1]} {predicate} {obj[1]}" 
    elif predicate == 'showInference':
        predicate = 'show inference'
        return f"{subject[1]} {predicate} {obj[1]}" 
    elif predicate == 'references':
        return f"{subject[1]} {predicate} {obj[1]}" 
    elif predicate == 'hasTopic':
        predicate = "has topic"
        return f"{subject[1]} {predicate} {obj[1]}" 
    elif predicate == 'follows':
        return f"{subject[1]} {predicate} {obj[1]}" 
    else:
        print("Error in search validation: Invalid relationship.")
    
    return "" 

def format_opposing_triplet(triplet):
    """
    Converts a structured triplet into a opposing human-readable query.
    The opposing search is based on the relationship and will switch the 
    entities to make an opposing search.

    Example:
    ('device', 'Govee Smart LED Light Bars') performs ('process', 'location tracking')
    → "Govee Smart LED Light Bars DOES NOT perform location tracking"
    """
    subject, predicate, obj = triplet

    if predicate == 'developedBy':
        predicate = 'is not developed by'
        return f"{subject[1]} {predicate} {obj[1]}"
    elif predicate == 'manufacturedBy':
        predicate = 'is not manufactured by'
        return f"{obj[1]} {predicate} {subject[1]}"
    elif predicate == 'compatibleWith':
        predicate = 'is not compatible with'
        return f"{subject[1]} {predicate} {obj[1]}" 
    elif predicate == 'hasSensor':
        predicate = 'does not have'
        return f"{subject[1]} {predicate} {obj[1]}" 
    elif predicate == 'accessSensor':
        predicate = "can not access"
        return f"{subject[1]} {predicate} {obj[1]}" 
    elif predicate == 'requiresSensor':
        predicate = "does not require"
        return f"{subject[1]} {predicate} {obj[1]}" 
    elif predicate == 'performs':
        predicate = "does not perfor,m"
        return f"{subject[1]} {predicate} {obj[1]}" 
    elif predicate == 'hasPolicy':
        predicate = 'does not jave policy'
        return f"{subject[1]} {predicate} {obj[1]}" 
    elif predicate == 'statesInPolicy':
        predicate = 'does not state that there is'
        return f"{obj[1]} {predicate} {subject[1]}" 
    elif predicate == 'captures':
        predicate = "does not capture"
        return f"{subject[1]} {predicate} {obj[1]}" 
    elif predicate == 'canInfer':
        predicate = 'can not infer'
        return f"{subject[1]} {predicate} {obj[1]}" 
    elif predicate == 'showInference':
        predicate = 'does not show inference'
        return f"{subject[1]} {predicate} {obj[1]}" 
    elif predicate == 'references':
        return f"{subject[1]} {predicate} {obj[1]}" 
    elif predicate == 'hasTopic':
        predicate = "does not have topic"
        return f"{subject[1]} {predicate} {obj[1]}" 
    elif predicate == 'follows':
        predicate = "does not follow"
        return f"{subject[1]} {predicate} {obj[1]}" 
    else:
        print("Error in search validation: Invalid relationship.")
    
    return ""

def get_total_search_results(query):
    """
    Uses selenium to search for the query and grabs the 'result-stats' id tag that
    Google uses to provide an approximate number of search results
    """
    
    options = Options()
    options.headless = True
    fake_useragent = UserAgent()
    options.binary_location = os.getenv('CHROME_PATH')
    options.add_argument(f'user-agent={fake_useragent.random}')
    options.add_argument('--disable-blink-features=AutomationControlled') 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
        
    driver = webdriver.Chrome(options=options)
    driver.get('https://www.google.com')
    wait = WebDriverWait(driver, 30)

    search = driver.find_element("name", "q")
    search.send_keys(query)
    search.send_keys(Keys.RETURN)

    try:
        totalUrls = wait.until(EC.presence_of_element_located((By.ID, "result-stats")))
        
        total_html = totalUrls.get_attribute('outerHTML')
        match = re.search(r'About\s+([\d,]+)\s+results', total_html)
        if match:
            number = int(match.group(1).replace(',', ''))
        else:
            number = -1

        return number

    
    except Exception as e:
        print("Error: result-stats not found or empty.", e)
    driver.quit()
    return -1

def main():

    triplets = get_triplets("triplets.txt")

    for triplet in triplets[:2]:
        query = format_triplet(triplet)
        opposingQuery = format_opposing_triplet(triplet)

        normalResults = -1        
        while(normalResults < 0):
            normalResults = get_total_search_results(query)

        opposingResults = -1
        while(opposingResults < 0):
            opposingResults = get_total_search_results(opposingQuery)

        print(query)
        print(opposingQuery)
        print(normalResults)
        print(opposingResults)

        weight = (normalResults + opposingResults) / 2
        print(weight)

if __name__ == "__main__":
    main()