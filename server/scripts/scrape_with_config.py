import argparse
import os
import json
import requests
from bs4 import BeautifulSoup
import time
from tqdm import tqdm
#from util.scraper.browser import get_chrome_driver
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import pandas as pd
from io import StringIO



CONFIGS_FOLDER = "config_files"

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

        print(f"URL {url}")
        # scrapes from text
        for tag in configs["text_content"]:
            if tag != "buttons":
                content = None
                if isinstance(configs["text_content"][tag], list):
                    for selector in configs["text_content"][tag]:
                        try:
                            print(f"Trying selector: {selector}")
                            element = page.locator(selector)
                            if element.count() > 0:
                                try:
                                    element.first.wait_for(timeout=5000)
                                    if element.first.is_visible():
                                        content = element.first.text_content()
                                        print(f"✅ Found selector for '{tag}': {selector}")
                                        break
                                except Exception as e:
                                    print(f"⚠️ Error waiting for or reading selector '{selector}': {e}")
                        except Exception as e:
                            print(f"Not found selector: {selector}")
                            continue
                else:
                    try:
                        print(f"Finding {configs["text_content"][tag]} for {tag}")
                        content = page.locator(configs["text_content"][tag]).first.text_content()
                        if not content:
                            content = page.locator(configs["text_content"][tag]).inner_text()
                    except Exception as e:
                        print(f"Unable to extract {tag}. {e}")
                        content = None

                if content:
                    text[tag] = "|".join(content.strip().split("\n"))
                else:
                    print(f"No content found for tag: {tag}")

        # clicks buttons to extract more text
        if "buttons" in configs["text_content"]:
            for button in configs["text_content"]["buttons"]:
                for button_selector, content_selector in configs["text_content"]["buttons"][button].items():
                    try:
                        button_elem = page.locator(button_selector)
                        button_elem.wait_for(timeout=5000)
                        button_elem.scroll_into_view_if_needed()
                        time.sleep(1)
                        button_elem.click()
                        print(f"Clicked on {button}")
                        time.sleep(3)
                        if content_selector == "table":
                            soup = BeautifulSoup(page.content(), features="lxml")
                            tables = soup.select("table")
                            #tables = table_html.select("table")
                            dfs = []
                            for i, table in enumerate(tables):
                                try:
                                    df = pd.read_html(StringIO(str(table)))[0]
                                    dfs.append(df)
                                    #print(f"\n📋 Table {i}:\n", df.to_string(index=False))
                                except ValueError:
                                    print(f"⚠️ Skipping unreadable table {i}")
                                    continue
                            #tables = pd.read_html(StringIO(str(table_html)))
                            if dfs:
                                combined = pd.concat(dfs, ignore_index=True)
                                content = combined.to_string(index=False)
                                text[button] = content
                                break
                            else:
                                print(f"❌ No readable tables found after clicking '{button}'")
                        else:
                            content = page.locator(content_selector).first.text_content()
                            if content:
                                text[button] = "|".join(content.strip().split("\n"))
                                break
                    except Exception as e:
                        print(f"Could not click or extract for button '{button}': {e}")

                    # reload the page
                    page.goto(url, timeout=120_000, wait_until="domcontentloaded")
                    time.sleep(2)

        browser.close()
        return str(text)

    
if __name__ == "__main__":
    # initializes argument parser
    parser = argparse.ArgumentParser(description="Process an input file and save output.")
    
    # Adding input and output arguments
    parser.add_argument("--config_file", required=True, help="json with configurations to a specific site")
    parser.add_argument("--batch_file", required=True, help="path to obtain the batch urls")
    parser.add_argument("--output_file", required=True, help="file to keep the output")

    # parses the arguments
    args = parser.parse_args()

    # sets the input and output files
    config_file = args.config_file
    batch_file = args.batch_file
    output_file = args.output_file

    with open(batch_file, "r") as f:
        product_urls = f.readlines()

    # extracts the contents of the configs file
    with open(os.path.join(CONFIGS_FOLDER, config_file), 'r') as f:
        configs = json.load(f)

    with open(output_file, "a", encoding="utf-8") as f:
        for url in tqdm(product_urls):
            url = url.strip()

            print(f"URL {url}")

            text_content = scrape_website(url, configs)
            print(text_content)
            
            f.write(f"{text_content} {url}\n")

