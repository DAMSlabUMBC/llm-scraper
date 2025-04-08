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

from transformers import BartForSequenceClassification, BartTokenizer
tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-mnli')
model = BartForSequenceClassification.from_pretrained('facebook/bart-large-mnli')

# Load environment variables
load_dotenv()

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

    
    driver = get_chrome_driver()
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
    # pose sequence as a NLI premise and label (politics) as a hypothesis
    premise = text
    hypothesis = f"This text is about {query}"

    # run through model pre-trained on MNLI
    input_ids = tokenizer.encode(premise, hypothesis, return_tensors='pt')
    logits = model(input_ids)[0]

    # we throw away "neutral" (dim 1) and take the probability of
    # "entailment" (2) as the probability of the label being true 
    entail_contradiction_logits = logits[:,[0,2]]
    probs = entail_contradiction_logits.softmax(dim=1)
    true_prob = probs[:,1].item() * 100
    print(f'Probability that the label is true: {true_prob:0.2f}%')

    return 69

def main():

    triplets = get_triplets("triplets.txt")

    for triplet in triplets[:2]:
        query = format_triplet(triplet)
        urls = get_urls(query)

        print(f"\n🔍 **Query:** {query}")

        for url in urls:

            # Text content from url
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')
            text_elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'p'])
            text_content = '\n'.join([elem.get_text() for elem in text_elements])

            # pose sequence as a NLI premise and label (politics) as a hypothesis
            premise = text_content
            hypothesis = query

            # run through model pre-trained on MNLI
            input_ids = tokenizer.encode(premise, hypothesis, return_tensors='pt')
            logits = model(input_ids)[0]

            # we throw away "neutral" (dim 1) and take the probability of
            # "entailment" (2) as the probability of the label being true 
            entail_contradiction_logits = logits[:,[0,2]]
            probs = entail_contradiction_logits.softmax(dim=1)
            true_prob = probs[:,1].item() * 100

            print("Probability: ", true_prob)

        #     # Compute SBERT-based semantic similarity
        #     similarity_score = compute_semantic_similarity(query, text_content)

        #     print(f"\n🔎 Query: {query}" )
        #     print(f"🔗 URL: {url}")
        #     print(f"📊 Relevance Score: {similarity_score}%")
        #     print("-" * 60)

if __name__ == "__main__":
    main()
