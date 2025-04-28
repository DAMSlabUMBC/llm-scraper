import argparse
import os
import json
import requests
from bs4 import BeautifulSoup
import time
from tqdm import tqdm
from util.scraper.browser import get_chrome_driver
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


CONFIGS_FOLDER = "config_files"

def scrape_website(url, configs):

    text = {}

    # opens playwright driver for scraping
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        try:
            page.goto(url, timeout=120_000, wait_until="domcontentloaded")  # 120 seconds
        except PlaywrightTimeout:
            print(f"⚠️ Timeout loading {url}")
            browser.close()
            return str(text)

        print(f"URL {url}")
        # scrapes from text
        for tag in configs["text"]:
            if tag != "buttons":
                content = None
                if isinstance(configs["text"][tag], list):
                    for selector in configs["text"][tag]:
                        try:
                            print(f"Trying selector: {selector}")
                            element = page.locator(selector)
                            if element.count() > 0:
                                content = element.first.text_content()
                                print(f"Found selector: {selector}")
                                break
                        except Exception as e:
                            print(f"Not found selector: {selector}")
                            continue
                else:
                    try:
                        content = page.locator(configs["text"][tag]).first.text_content()
                    except Exception:
                        content = None

                if content:
                    text[tag] = "|".join(content.strip().split("\n"))
                else:
                    print(f"No content found for tag: {tag}")

        # clicks buttons to extract more text
        if "buttons" in configs["text"]:
            for button in configs["text"]["buttons"]:
                for button_selector, content_selector in configs["text"]["buttons"][button].items():
                    try:
                        button_elem = page.locator(button_selector)
                        button_elem.scroll_into_view_if_needed()
                        time.sleep(1)
                        button_elem.click()
                        time.sleep(3)
                        content = page.locator(content_selector).first.text_content()
                        if content:
                            text[button] = "|".join(content.strip().split("\n"))
                    except Exception as e:
                        print(f"Could not click or extract for button '{button}': {e}")

                    # reload the page
                    page.goto(url, timeout=120_000, wait_until="domcontentloaded")
                    time.sleep(2)

        browser.close()
        return str(text)

