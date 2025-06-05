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
from selenium.common.exceptions import StaleElementReferenceException
import threading
from urllib.parse import urlparse
import time

import re

from transformers import BartForSequenceClassification, BartTokenizer
tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-mnli')
model = BartForSequenceClassification.from_pretrained('facebook/bart-large-mnli')

# Load environment variables
load_dotenv()

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

def get_urls(query, max_results=5):
    driver = get_chrome_driver()
    driver.get('https://www.google.com')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "q")))

    search = driver.find_element("name", "q")
    search.send_keys(query, Keys.RETURN)
    anchors = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))

    urls, seen = [], set()
    for a in anchors:
        href = a.get_attribute("href")
        if not href or href in seen:
            continue
        parsed = urlparse(href)
        if parsed.netloc.startswith("www.google.com"):
            continue
        urls.append(href); seen.add(href)
        if len(urls) >= max_results:
            break

    driver.quit()
    return urls

def entailment_score(premise: str, hypothesis: str) -> float:
    """Return entailment % from BART-MNLI."""
    inputs = tokenizer.encode(premise, hypothesis, return_tensors='pt',
                              truncation=True, max_length=1024)
    logits = model(inputs)[0]
    # logits dims: [batch, 3] → [contradiction, neutral, entailment]
    # we pick indices [0, 2] then softmax → entailment prob
    entail_contra = logits[:, [0, 2]]
    probs = entail_contra.softmax(dim=1)
    return probs[:, 1].item() * 100

def llm_validation_method(triple):
    subject, predicate, obj = triple
    query = f"{subject[1]} {predicate} {obj[1]}"
    urls = get_urls(query)

    print(f"\n🔍 Query: {query}")
    all_scores = []

    for url in urls:
        print("Visiting:", url)
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        text = "\n".join(elem.get_text() for elem in soup.find_all(['p','span','h1','h2','h3']))

        # 1) exact‐match regex check
        if re.search(r"manufactur.*Govee", text, re.IGNORECASE):
            print("→ Found direct “manufactured by Govee” match in raw text.")
            return 100.0

        # 2) split into sentences to focus NLI on smaller chunks
        sentences = re.split(r'(?<=[\.\?\!])\s+', text)
        for sent in sentences:
            if len(sent) < 20:
                continue   # skip very short fragments
            score = entailment_score(sent, query)
            all_scores.append(score)

    if not all_scores:
        print("No candidate sentences found; returning 0%.")
        return 0.0

    final_score = max(all_scores)
    print(f"Aggregated entailment probability: {final_score:0.2f}%")
    return final_score