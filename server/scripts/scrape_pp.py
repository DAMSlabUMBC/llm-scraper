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
from analysis.entity_analysis import analyze_text_elements
from analysis.relationship_analysis import generate
import ast
from util.llm_utils.response_cleaner import parse_string_to_list

CONFIGS_FOLDER = "config_files"
PROMPTS_FOLDER = "prompts"
RETRIES = 3

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

        # saves the html code in a file
        with open("google_pp.html", "w", encoding="utf-8") as f:
            f.write(html_code)

        soup = BeautifulSoup(html_code, "html.parser")

        # extracts all text in the privacy policy
        extracted_text = []
        for tag in soup.find_all(['h1', 'h2', 'h3', 'p']):
            if tag.get_text(strip=True) != "":
                print(f"{tag.name.upper()}: {tag.get_text(strip=True)}")
                extracted_text.append(f"{tag.name.upper()}: {tag.get_text(strip=True)}")

        #print(f'EXTRACTED TEXT {extracted_text}')

        # matches headings with their text
        text_content = flush_extracted_text(extracted_text)


        return text_content

def clean_triples(triples, configs):
    new_triples = []
    for triple in triples:

        # converts the string into a tuple
        triple = ast.literal_eval(triple)
        
        # splits the triple by their subject, object, and predicate
        subj, pred, obj = triple[0], triple[1], triple[2]

        new_pred = pred

        # print(f"SUBJECT {subj}")
        # print(f"PREDICATE {pred}")
        # print(f"OBJECT {obj}")

        # splits subject by entity type and same
        subj_type, subj_name = subj[0], subj[1]
        new_subj_type = subj_type
        new_subj_name = subj_name

        if subj_name.lower() in configs["keywords"]:
            new_subj_name = configs["keywords"][subj_name.lower()]

        # splits object by entity type and same
        obj_type, obj_name = obj[0], obj[1]
        new_obj_type = obj_type
        new_obj_name = obj_name

        if obj_name.lower() in configs["keywords"]:
            new_obj_name = configs["keywords"][obj_name.lower()]

        new_triple = (new_subj_type, new_subj_name), new_pred, (new_obj_type, new_obj_name)

        new_triples.append(new_triple)

    return new_triples

    
if __name__ == "__main__":
    # initializes argument parser
    parser = argparse.ArgumentParser(description="Process an input file and save output.")
    
    # Adding input and output arguments
    parser.add_argument("--config_file", required=True, help="json with configurations to a specific site")
    parser.add_argument("--output_file", required=True, help="file to keep the output")
    parser.add_argument("--ollama_port", type=int, help="Port number for Ollama")

    # parses the arguments
    args = parser.parse_args()

    # sets the input and output files
    config_file = args.config_file
    #batch_file = args.batch_file
    output_file = args.output_file

    # extracts the contents of the configs file
    with open(os.path.join(CONFIGS_FOLDER, config_file), 'r') as f:
        configs = json.load(f)

    # gets the appropriate prompts for the specific website
    with open(os.path.join(PROMPTS_FOLDER, configs["type"], "entity_analysis.txt"), "r", encoding="utf-8") as f:
        entity_prompt = f.read()

    with open(os.path.join(PROMPTS_FOLDER, configs["type"], "relationship_analysis.txt"), "r", encoding="utf-8") as f:
        relationship_prompt = f.read()

    url = configs["home_url"]

    # text_content = scrape_website(url, configs)

    # for tag in text_content:
    #     print(f"T: {tag}")
    #     print(f"C: {text_content[tag]}")

    extract_file = configs["extracted_content"]
    # with open(extract_file, "w", encoding="utf-8") as f:
    #     f.write(f"{text_content} {url}")

    with open(extract_file, "r", encoding="utf-8") as f:
        content = f.read()

    text_content, url = content.rsplit(" ", 1)

    # print(f"TEXT CONTENT {text_content}")
    # print(f"URL {url}")

    text_dict = ast.literal_eval(text_content)

    count = 0

    with open(output_file, "w", encoding="utf-8") as f:
        for tag in tqdm(text_dict):
            text = f"{tag}: {text_dict[tag]}"
            #print(text)
            entities = analyze_text_elements(text, entity_prompt)
    
            # generates triplets for number of retries
            for i in range(RETRIES):
    
                # generates triplets
                generate_result = generate(str(entities), relationship_prompt, text)
    
                result_list = parse_string_to_list(generate_result)
                if isinstance(result_list, list):
                    if result_list != []:
                        break
            
            # returns empty list of triplets if fails to generate entities for number of retries
            if not isinstance(result_list, list):
                result_list = []
                count += 1
    
            print(f"TRIPLES BEFORE: {result_list}")
    
            result_list = clean_triples(result_list, configs)
    
            print('[😻] Final Response: ', result_list)
            f.write(f"{text} {result_list}\n")
            # for triple in result_list:
            #     f.write(f"{triple} {url}\n")
            #print(f"ENTITIES: {entities}")

    print(f"MISSING TRIPLETS: {count}")
