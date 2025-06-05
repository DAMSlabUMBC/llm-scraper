import requests
import random
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

from dotenv import load_dotenv
from arango import ArangoClient

# Load environment variables
load_dotenv()

client = ArangoClient(hosts=os.getenv("HOST_URL"))

db = client.db(
    "_system",
    username=os.getenv("ARRANGODB_USERNAME"),
    password=os.getenv("ARRANGODB_PASSWORD"),
)

graph = db.graph("IoT_KG")

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

# https://docs.arangodb.com/3.12/aql/data-queries/
def top_by_edge(edge_col, vertex_col, direction="INBOUND", limit=3):
    query = f"""
            FOR v IN `{vertex_col}`
            LET edgeCount = LENGTH(
                FOR w IN 1..1 {direction} v `{edge_col}`
                RETURN 1
            )
            SORT edgeCount DESC
            LIMIT @limit
            RETURN {{ name: v.name, count: edgeCount }}
            """
    return list(db.aql.execute(query, bind_vars={"limit": limit}))

def format_opposing_triplet(triplet):

    subject, predicate, obj = triplet
    subject = list(subject)
    obj = list(obj)

    choice = ""
    my_vertex = ""
    result = []

    # TODO: Determine which node to corrupt for opposing search
    if random.random() < 0.50:
        choice = "subject"
        my_vertex = subject[0]
    else:
        choice = "obj"
        my_vertex = obj[0]


    tops = top_by_edge(
        edge_col=predicate,
        vertex_col=my_vertex,
        direction="INBOUND",
        limit=5
    )

    for doc in tops:
        print(doc["name"], "→", doc["count"], "devices")

        if doc["name"] == subject[1] or doc["name"] == obj[1]:
            continue
        if len(result) >= 3:
            break

        if choice == "subject":
            subject[1] = doc["name"]
        else:
            obj[1] = doc["name"]
        new_triplet = subject, predicate, obj
        result.append(format_triplet(new_triplet))

    print(tops)

    print("✅ FINAL: ",result)
    return result

def get_total_search_results(driver, query):
    """
    Uses selenium to search for the query and grabs the 'result-stats' id tag that
    Google uses to provide an approximate number of search results
    """
    
    driver.get('https://www.google.com')
    wait = WebDriverWait(driver, 10)

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
    return -1

def search_validation_method(triple):
    driver = get_chrome_driver()

    try:
        query = format_triplet(triple)
        opposingQuery = format_opposing_triplet(triple)

        print(query)
        print(opposingQuery)

        normalResults = 0        
        opposingResults = 0
        totalResults = 0;

        for q in query:
            result = get_total_search_results(driver, q)
            if result > normalResults:
                normalResults = result
            print("Top normal result: ", normalResults)
            totalResults += result

        for set in opposingQuery:
            for q in set:
                result = get_total_search_results(driver, q)
                if result > opposingResults:
                    opposingResults = result
                print("Top opposing result: ", opposingResults)
                totalResults += result
            
        
        print(normalResults)
        print(opposingResults)

        total = normalResults + opposingResults 
        weight = normalResults / total if total else 0

        print(weight)
        return weight
    finally:
        driver.quit()

# def main():

#     driver = get_chrome_driver()

#     try:
#         triplets = get_triplets("triplets.txt")

#         for triplet in triplets[:1]:
#             query = format_triplet(triplet)
#             opposingQuery = format_opposing_triplet(triplet)

#             print(query)
#             print(opposingQuery)

#             normalResults = 0        
#             opposingResults = 0
#             totalResults = 0;

#             for q in query:
#                 result = get_total_search_results(driver, q)
#                 if result > normalResults:
#                     normalResults = result
#                 print("Top normal result: ", normalResults)
#                 totalResults += result

#             for set in opposingQuery:
#                 for q in set:
#                     result = get_total_search_results(driver, q)
#                     if result > opposingResults:
#                         opposingResults = result
#                     print("Top opposing result: ", opposingResults)
#                     totalResults += result
                
            
#             print(normalResults)
#             print(opposingResults)

#             weight = normalResults / (normalResults + opposingResults)

#             # TODO: Write to a file the weight
#             print(weight)
#     finally:
#         driver.quit()

# if __name__ == "__main__":
#     main()