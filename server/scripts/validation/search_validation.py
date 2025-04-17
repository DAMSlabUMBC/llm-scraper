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
from util.scraper.browser import get_chrome_driver

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
    # Unpack the triple into its components.
    (subject_type, subject_value), predicate, (object_type, object_value) = triplet
    variants = []
    
    if predicate == 'hasSensor' and subject_type == 'device' and object_type == 'sensor':
        variants = [
            f"{subject_value} has {object_value}",
            f"{subject_value} is equipped with {object_value}",
            f"{object_value} is part of {subject_value}",
            f"{subject_value} comes with {object_value}",
            f"{subject_value} features {object_value}"
        ]
    elif predicate == 'manufacturedBy' and subject_type == 'device' and object_type == 'manufacturer':
        variants = [
            f"{subject_value} is manufactured by {object_value}",
            f"{subject_value} is produced by {object_value}",
            f"{subject_value} comes from {object_value}",
            f"{object_value} manufactures {subject_value}",
            f"{subject_value} is built by {object_value}"
        ]
    elif predicate == 'compatibleWith':
        variants = [
            f"{subject_value} is compatible with {object_value}",
            f"{subject_value} works with {object_value}",
            f"{object_value} is supported by {subject_value}",
            f"{subject_value} pairs with {object_value}",
            f"{subject_value} integrates well with {object_value}"
        ]
    elif predicate == 'performs' and subject_type == 'device' and object_type == 'process':
        variants = [
            f"{subject_value} performs {object_value}",
            f"{subject_value} carries out {object_value}",
            f"{subject_value} executes {object_value}",
            f"{subject_value} completes {object_value}",
            f"{subject_value} undertakes {object_value}"
        ]
    elif predicate == 'hasPolicy':
        variants = [
            f"{subject_value} has policy {object_value}",
            f"{subject_value} adopts the {object_value} policy",
            f"{subject_value} follows the {object_value} policy",
            f"{subject_value} implements the {object_value} policy",
            f"{subject_value} operates under the {object_value} policy"
        ]
    elif predicate == 'statesInPolicy' and object_type == 'privacyPolicy':
        variants = [
            f"{subject_value} is stated in policy {object_value}",
            f"Policy {object_value} specifies {subject_value}",
            f"Policy {object_value} outlines {subject_value}",
            f"{subject_value} is mentioned in policy {object_value}",
            f"{subject_value} is detailed in policy {object_value}"
        ]
    elif predicate == 'follows' and subject_type == 'privacyPolicy' and object_type == 'regulation':
        variants = [
            f"{subject_value} follows {object_value}",
            f"{subject_value} adheres to {object_value}",
            f"{subject_value} complies with {object_value}",
            f"{subject_value} upholds {object_value}",
            f"{subject_value} observes {object_value}"
        ]
    elif predicate == 'developedBy' and subject_type == 'application' and object_type == 'manufacturer':
        variants = [
            f"{subject_value} is developed by {object_value}",
            f"{object_value} develops {subject_value}",
            f"{subject_value} is created by {object_value}",
            f"{subject_value} is engineered by {object_value}",
            f"{subject_value} is built under the guidance of {object_value}"
        ]

    return variants

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
    
    driver = get_chrome_driver()
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