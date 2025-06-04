import argparse
import os
import json
import requests
from bs4 import BeautifulSoup
import time
from tqdm import tqdm
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import pandas as pd
from io import StringIO



CONFIGS_FOLDER = "config_files"

HEADINGS = ["H1", "H2", "H3"]
CONTENT = ["P"]

def flush_extracted_text(extracted_text):

    prev = "H1"
    key = ""
    value = ""
    text_content = {}
    for text in extracted_text:
        tag, content = text.split(":", 1)

        if prev in HEADINGS and tag in HEADINGS:
            key += f" -> {content}"
        elif prev in CONTENT and tag in CONTENT:
            value += f" {content.strip()}"
        elif prev in HEADINGS and tag in CONTENT:
            value += content
        elif prev in CONTENT and tag in HEADINGS:
            text_content[key] = value
            key = content
            value = ""
        prev = tag
    
    #print(f"TEXT CONTENT {text_content}")

    # for tag in text_content:
    #     #print(f"{tag} {text_content[tag]}")
    #     print(f"TAG {tag}")
    #     print(f"CONTENT: {text_content[tag]}")

    return text_content

def scrape_website(url, configs):

    text = {}

    # opens playwright driver for scraping
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
            java_script_enabled=True,
            locale="en-US",
            timezone_id="America/New_York",
            device_scale_factor=1,
        )
        page = context.new_page()

        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.navigator.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
        """)

        # lazy scrolling
        for _ in range(3):
            page.mouse.wheel(0, 1000)
            time.sleep(1)

        try:
            page.goto(url, timeout=120_000, wait_until="domcontentloaded")  # 120 seconds
        except PlaywrightTimeout:
            print(f"⚠️ Timeout loading {url}")
            browser.close()
            return str(text)
        
        # checks if the page is unavailable
        for tag in configs.get("skip", []):
            element = page.locator(tag)

            if element:
                text_content = element.text_content() or ""
                if configs["skip"][tag] in text_content:
                    print(f"Skipping unavailable url: {url}")
                    browser.close()
                    return str(text)
                
        html_code = page.content()

        with open("google_pp.html", "w", encoding="utf-8") as f:
            f.write(html_code)
                
        
        # response = requests.get(url)

        # if response.status_code == 200:
        #     html_code = response.text
        #     with open("google_pp.html", "w", encoding="utf-8") as f:
        #         f.write(html_code)
        # else:
        #     print(f"Request failed with status code {response.status_code}")

        soup = BeautifulSoup(html_code, "html.parser")

        extracted_text = []
        for tag in soup.find_all(['h1', 'h2', 'h3', 'p']):
            if tag.get_text(strip=True) != "":
                print(f"{tag.name.upper()}: {tag.get_text(strip=True)}")
                extracted_text.append(f"{tag.name.upper()}: {tag.get_text(strip=True)}")

        #print(f'EXTRACTED TEXT {extracted_text}')

        text_content = flush_extracted_text(extracted_text)

        # for tag in text_content:
        #     print(f"TAG {tag}")
        #     print(f"CONTENT {text_content[tag]}")

        return text_content

    
if __name__ == "__main__":
    # initializes argument parser
    parser = argparse.ArgumentParser(description="Process an input file and save output.")
    
    # Adding input and output arguments
    parser.add_argument("--config_file", required=True, help="json with configurations to a specific site")
    #parser.add_argument("--batch_file", required=True, help="path to obtain the batch urls")
    #parser.add_argument("--output_file", required=True, help="file to keep the output")

    # parses the arguments
    args = parser.parse_args()

    # sets the input and output files
    config_file = args.config_file
    #batch_file = args.batch_file
    #output_file = args.output_file

    # with open(batch_file, "r") as f:
    #     product_urls = f.readlines()

    # extracts the contents of the configs file
    with open(os.path.join(CONFIGS_FOLDER, config_file), 'r') as f:
        configs = json.load(f)

    url = configs["home_url"]

    text_content = scrape_website(url, configs)

    for tag in text_content:
        print(f"T: {tag}")
        print(f"C: {text_content[tag]}")

    extract_file = configs["extracted_content"]
    with open(extract_file, "w", encoding="utf-8") as f:
        f.write(f"{text_content} {url}")
