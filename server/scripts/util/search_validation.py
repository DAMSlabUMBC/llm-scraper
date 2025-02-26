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

# Load environment variables
load_dotenv()

# Load a pretrained Sentence Transformer model
device = "cuda" if torch.cuda.is_available() else "cpu"
model = SentenceTransformer("all-mpnet-base-v2").to(device)

def get_urls(query):

    result = []
    seen = set()

    excluded_domains = {
        "www.google.com",
        "accounts.google.com",
        "support.google.com",
        "policies.google.com",
        "search.app.goo.gl",
        "maps.google.com",
    }
    
    excluded_paths = {
        "/search",
        "/advanced_search",
        "/ServiceLogin",
    }

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
    wait = WebDriverWait(driver, 10)

    search = driver.find_element("name", "q")
    search.send_keys(query)
    search.send_keys(Keys.RETURN)
    anchor_elements = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))
    count = 0
    for element in anchor_elements:
        if count >= 5:
            break
        href = element.get_attribute("href")
        if href is None:
            continue
        parsed = urlparse(href)
        domain = parsed.netloc
        path = parsed.path
        if domain not in excluded_domains and path not in excluded_paths:
            if href not in seen:
                print(href)
                result.append(href)
                seen.add(href)
                count += 1

    time.sleep(5)
    driver.quit()
    return result

def get_triplets(filename):

    """
    Function to grab the triplets from the file

    :param filename: Text file containing triplets
    :return: Triplets from each line
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
    return f"{subject[1]} {predicate} {obj[1]}" 

def compute_semantic_similarity(query, text):
    """
    Computes the semantic similarity between the query and the snippet using SBERT embeddings.

    :param query: Query string.
    :param snippet: Search result snippet.
    :return: Cosine similarity score (0 to 100%).
    """
    query_embedding = model.encode(query, convert_to_tensor=True)
    text_embedding = model.encode(text, convert_to_tensor=True)

    cosine_score = util.pytorch_cos_sim(query_embedding, text_embedding).item()
    return round(cosine_score * 100, 2)

def main():

    triplets = get_triplets("triplets.txt")

    for triplet in triplets[:3]:
        query = format_triplet(triplet)
        urls = get_urls(query)

        print(f"\n🔍 **Query:** {query}")

        for url in urls:

            # Text content from url
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')
            text_elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'p'])
            text_content = '\n'.join([elem.get_text() for elem in text_elements])

            # Compute SBERT-based semantic similarity
            similarity_score = compute_semantic_similarity(query, text_content)

            print(f"\n🔎 Query: {query}" )
            print(f"🔗 URL: {url}")
            print(f"📊 Relevance Score: {similarity_score}%")
            print("-" * 60)

if __name__ == "__main__":
    main()
