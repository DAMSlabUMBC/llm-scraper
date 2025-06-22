import requests
import os
import ast
import re
from urllib.parse import urlparse

from dotenv import load_dotenv
from bs4 import BeautifulSoup
from transformers import BartForSequenceClassification, BartTokenizer
from sentence_transformers import SentenceTransformer, util

import torch
from playwright.sync_api import sync_playwright

# Load environment variables
load_dotenv()

# Load NLI model
tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-mnli')
model = BartForSequenceClassification.from_pretrained('facebook/bart-large-mnli')

def get_triplets(filename):
    with open(filename, "r", encoding="utf-8") as file:
        try:
            triplets = ast.literal_eval(file.read())
            return triplets
        except (SyntaxError, ValueError) as e:
            print(f"Error parsing file: {e}")
            return []

def format_triplet(triplet):
    subject, predicate, obj = triplet
    return f"{subject[1]} {predicate} {obj[1]}"

def get_urls(query, max_results=5):
    urls = []
    seen = set()
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path='/umbc/ada/ryus/users/gsantos2/tools/playwright_browsers/chromium-1161/chrome-linux/chrome'
        )
        page = browser.new_page()
        page.goto("https://www.google.com")
        page.fill("input[name='q']", query)
        page.keyboard.press("Enter")
        page.wait_for_selector("a", timeout=10000)

        anchors = page.query_selector_all("a")
        for a in anchors:
            href = a.get_attribute("href")
            if not href or href in seen:
                continue
            parsed = urlparse(href)
            if parsed.netloc.startswith("www.google.com"):
                continue
            urls.append(href)
            seen.add(href)
            if len(urls) >= max_results:
                break

        browser.close()
    return urls

def entailment_score(premise: str, hypothesis: str) -> float:
    inputs = tokenizer.encode(premise, hypothesis, return_tensors='pt', truncation=True, max_length=1024)
    logits = model(inputs)[0]
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
        try:
            page = requests.get(url, timeout=10)
            soup = BeautifulSoup(page.content, 'html.parser')
            text = "\n".join(elem.get_text() for elem in soup.find_all(['p', 'span', 'h1', 'h2', 'h3']))
        except Exception as e:
            print(f"Failed to retrieve or parse {url}: {e}")
            continue

        if re.search(rf"{predicate}.*{obj[1]}", text, re.IGNORECASE):
            print(f"→ Found direct match: {predicate} {obj[1]} in raw text.")
            return 100.0

        sentences = re.split(r'(?<=[\.\?!])\s+', text)
        for sent in sentences:
            if len(sent) < 20:
                continue
            score = entailment_score(sent, query)
            all_scores.append(score)

    if not all_scores:
        print("No candidate sentences found; returning 0%.")
        return 0.0

    final_score = max(all_scores)
    print(f"Aggregated entailment probability: {final_score:0.2f}%")
    return final_score
