import argparse
import os
import json
import time
from tqdm import tqdm
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import random

CONFIGS_FOLDER = "config_files"
VISITED = []

def click_next(page, configs):
    try:
        print("🔍 Looking for next button with selector:", configs['eccomerce']["next"])
        page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        next_button = page.locator(configs["eccomerce"]["next"])
        if next_button.count() == 0:
            print("❌ Next button not found.")
            return None

        next_href = next_button.first.get_attribute("href")
        print(f"next_href {next_href}")
        if next_href and next_href != "#":
            full_url = urljoin(configs["home_url"], next_href)
            print("👉 Navigating to:", full_url)
            page.goto(full_url, timeout=60000)
        else:
            next_button.first.scroll_into_view_if_needed()
            next_button.first.click()
            #time.sleep(30)
            page.mouse.move(100, 200)
            page.mouse.wheel(0, 1500)
            time.sleep(1 + random.random() * 2)

        if page.url not in VISITED:
            VISITED.append(page.url)
            return BeautifulSoup(page.content(), "html.parser")
        return None

    except Exception as e:
        print("❌ Error in click_next:", e)
        return None

def main(config_file):
    with open(os.path.join(CONFIGS_FOLDER, config_file), 'r') as f:
        configs = json.load(f)

    print("📄 Loaded Config:", configs["eccomerce"]["product_urls"])

    with open("search_queries.txt", "r") as f:
        search_queries = [q.strip() for q in f.readlines()]

    product_urls = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--disable-http2"])
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
            Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
            Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
        """)

        page.goto(configs["home_url"], timeout=60000)
        page.wait_for_selector(configs["eccomerce"]["search_bar"], timeout=10000)

        search_box = page.locator(configs["eccomerce"]["search_bar"])

        with open(configs["temp_urls"], "a") as f:
            search_queries = ["smart cameras", "smart plugs"]
            #search_queries = search_queries[8:]
            for query in tqdm(search_queries):
                print(f"🔎 Searching for: {query}")
                try:
                    search_box.fill(query)
                    search_box.press("Enter")
                    #time.sleep(30)
                    page.mouse.move(100, 200)
                    page.mouse.wheel(0, 1500)
                    time.sleep(1 + random.random() * 2)

                    for _ in range(3):
                        page.mouse.wheel(0, 1000)
                        time.sleep(1)

                    soup = BeautifulSoup(page.content(), "html.parser")
                    product_elements = soup.select(configs["eccomerce"]["product_urls"])
                    print(f"🔗 Found {len(product_elements)} product links")

                    if len(product_elements) == 0:
                        with open("debug_no_products.html", "w", encoding="utf-8") as debug_f:
                            debug_f.write(page.content())
                        print("📄 Dumped page for inspection.")
                        continue

                    for product in product_elements:
                        href = product.get("href")
                        if href and href.startswith("/"):
                            full_url = configs["home_url"].rstrip("/") + href
                            f.write(full_url + "\n")
                            product_urls.add(full_url)

                    while True:
                        soup = click_next(page, configs)
                        if not soup:
                            break

                        product_elements = soup.select(configs["eccomerce"]["product_urls"])
                        for product in product_elements:
                            href = product.get("href")
                            if href and href.startswith("/"):
                                full_url = configs["home_url"].rstrip("/") + href
                                f.write(full_url + "\n")
                                product_urls.add(full_url)

                except Exception as e:
                    print(f"❌ Failed on query '{query}': {e}")
                    continue

                # Reload for next search
                page.goto(configs["home_url"], timeout=60000)
                page.wait_for_selector(configs["eccomerce"]["search_bar"], timeout=10000)
                search_box = page.locator(configs["eccomerce"]["search_bar"])

        browser.close()

    # Merge with existing URLs and write to official
    with open(configs["official_urls"], "r") as f:
        existing = set([line.strip() for line in f])
    product_urls.update(existing)

    with open(configs["official_urls"], "w") as f:
        for url in sorted(product_urls):
            f.write(url + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Playwright-based product URL extractor.")
    parser.add_argument("--config_file", required=True, help="Path to JSON config file")
    args = parser.parse_args()
    main(args.config_file)
