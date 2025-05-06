import asyncio
import json
import os
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import ollama
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from playwright.async_api import async_playwright

# === setup ===
os.makedirs("output", exist_ok=True)
URL = "https://www.target.com/p/nintendo-switch-2-console-mario-kart-world-bundle/-/A-94693226#lnk=sametab"
#URL = "https://www.amazon.com/Smart-Compatible-Assistant-Single-Pole-Certified/dp/B09JZ6W1BH"
#URL = "https://www.bestbuy.com/site/apple-geek-squad-certified-refurbished-airpods-4-with-active-noise-cancellation-white/6601300.p?skuId=6601300"

# === Schema Stuff ===
SCHEMAS = {
    "amazon.com": {
        "name": "amazon_product",
        "baseSelector": "#dp",
        "fields": [
            {"name": "title", "selector": "#productTitle", "type": "text"},
            {"name": "price", "selector": "span.a-price span.a-offscreen", "type": "text"},
            {"name": "rating", "selector": "span[data-hook='rating-out-of-text']", "type": "text"},
            {"name": "image", "selector": "#landingImage", "type": "attribute", "attribute": "src"},
        ]
    },
    "bestbuy.com": {
    "name": "bestbuy_product",
    "baseSelector": "div.sku-title",
    "fields": [
        {"name": "title", "selector": "h1.sku-title", "type": "text"},
        {"name": "price", "selector": "div.priceView-hero-price span", "type": "text"},
        {"name": "rating", "selector": "div.c-ratings-reviews-v4 span.c-reviews", "type": "text"},
        {"name": "image", "selector": "img.primary-image", "type": "attribute", "attribute": "src"},
        ]
    }
}

# === helper stuff ===
def schema_url(url: str):
    host = urlparse(url).netloc
    for domain in SCHEMAS:
        if domain in host:
            return JsonCssExtractionStrategy(SCHEMAS[domain])
    return None

def get_html(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    return response.text

def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(['script', 'style']):
        tag.decompose()
    return soup.get_text(separator=' ', strip=True)[:4000]


async def playwright_html(url: str) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_timeout(5000)
        content = await page.content()
        await browser.close()
        return content

def extract_playwright(html: str) -> dict:
    soup = BeautifulSoup(html, 'html.parser')

    def safe_select_text(selector):
        tag = soup.select_one(selector)
        return tag.text.strip() if tag else None

    def safe_select_attr(selector, attr):
        tag = soup.select_one(selector)
        return tag[attr] if tag and attr in tag.attrs else None

    data = {
        "title": safe_select_text("div.sku-title h1"),
        "price": safe_select_text("div.priceView-hero-price span"),
        "rating": safe_select_text("div.c-ratings-reviews-v4 span.c-reviews"),
        "image": safe_select_attr("img.primary-image", "src"),
    }

    return data if any(data.values()) else None

async def call_ollama(prompt: str) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: ollama.generate(
        model='gemma3',
        prompt=prompt
    )['response'])

async def main():
    schema = schema_url(URL)
    extracted = None

    # === CRAWL4AI ===
    print("Crawl4AI")
    if schema:
        try:
            async with AsyncWebCrawler() as crawler:
                config = CrawlerRunConfig()
                config.extraction_strategy = schema
                result = await crawler.arun(URL, config=config)
                extracted = json.loads(result.extracted_content)

                if extracted:
                    print("\n✅ Extracted with crawl4ai:")
                    print(json.dumps(extracted, indent=2))
                    with open("output/extracted_product.json", "w") as f:
                        json.dump(extracted, f, indent=2)
                    return  # ✅ Stop here completely if successful
                else:
                    print("⚠️ Crawl4AI empty result.")
        except Exception as e:
            print("❌ crawl4ai failed:", e)
            
    # === PLAYWRIGHT ===
    print("🔁 Playwright")
    try:
        rendered_html = await playwright_html(URL)
    
        # Save the rendered HTML for debugging
        with open("output/playwright_rendered.html", "w", encoding="utf-8") as f:
            f.write(rendered_html)
    
        product = extract_playwright(rendered_html)
        if product:
            print("\n✅ Extracted with Playwright:")
            print(json.dumps([product], indent=2))
            with open("output/playwright_product.json", "w") as f:
                json.dump([product], f, indent=2)
            return
        else:
            print("❌ Playwright empty result.")
    
    except Exception as e:
        print("❌ Playwright extraction failed:", e)

    # === AI ===
    if not extracted:
        print("🔁 AI extraction...")
        html = get_html(URL)
        clean_text = clean_html(html)

        prompt = f"""
You are a Named Entity Recognition (NER) system specialized in IoT and tech documentation.

From the following webpage content, extract entities in these categories:
- devices
- manufacturer
- price
- application
- process
- sensor
- observation
- inference
- research
- privacy policy
- regulation

### Output Rules:
- Return ONLY JSON: {{ "entities": [{{ "type": ..., "value": ... }}, ...] }}
- Do not explain anything.
- If no matches, return {{ "entities": [] }}

Website content:
\"\"\"{clean_text}\"\"\"
"""

        response = await call_ollama(prompt)
        print("\n🧠 Extracted with AI:")
        print(response)

        with open("output/llm_extracted_product.json", "w") as f:
            f.write(response)

asyncio.run(main())
