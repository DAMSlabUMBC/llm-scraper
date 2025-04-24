# amazon_scrape_with_ollama_save.py

import asyncio
import json
import os
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
import ollama

# folder organization
os.makedirs("output", exist_ok=True)

URL = "https://www.amazon.com/Smart-Compatible-Assistant-Single-Pole-Certified/dp/B09JZ6W1BH"

schema = {
    "name": "amazon_product",
    "baseSelector": "#dp",
    "fields": [
        {"name": "title",  "selector": "#productTitle", "type": "text"},
        {"name": "price",  "selector": "span.a-price span.a-offscreen", "type": "text"},
        {"name": "rating", "selector": "span[data-hook='rating-out-of-text']", "type": "text"},
        {"name": "image",  "selector": "#landingImage", "type": "attribute", "attribute": "src"},
    ],
}
extractor = JsonCssExtractionStrategy(schema)

async def call_ollama_gemma(prompt: str) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: ollama.generate(
        model='gemma3',
        prompt=prompt
    )['response'])

async def main():
    async with AsyncWebCrawler() as crawler:
        res = await crawler.arun(URL, config=CrawlerRunConfig(extraction_strategy=extractor))
        extracted = json.loads(res.extracted_content)
        print("Extracted Stuff:\n", json.dumps(extracted, indent=2))

        if not extracted:
            print("No data extracted.")
            return

        # Save extracted JSON to file
        with open("output/extracted_product.json", "w") as f:
            json.dump(extracted, f, indent=2)

        product = extracted[0]

# prompt
        prompt = f"""
You are an expert in product analysis and You are a Named Entity Recognition (NER) Specialist that extracts IoT-related entities from given text. The extracted entities must fit into one of these categories:
- devices
- manufacturer
- application
- process
- sensor
- observation
- inference
- research
- privacy policy
- regulation

### Output Rules:
- Output strictly in the JSON format: {{ "entities": [list of entities] }}
- Do **not** include explanations, reasoning, or extra text.
- Do **not** use the word "json" in the output.
- If no entities are found, return {{ "entities": [] }}

Product Info:
Title: {product.get("title")}
Price: {product.get("price")}
Rating: {product.get("rating")}
Image URL: {product.get("image")}

### Example Outputs:

**Example 1:**
Input: "Amazon Echo Dot, With Alexa, Charcoal."
Output:
{{"entities": ["Amazon", "Alexa", "Amazon Echo Dot", "Speaker", "voice assistant"]}}

**Example 2:**
Input: "There are no entities here."
Output:
{{"entities": []}}
"""

        gemma_response = await call_ollama_gemma(prompt)

        print("\nGemma AI Response:\n", gemma_response)

        # Save response
        with open("output/gemma_summary.txt", "w") as f:
            f.write(gemma_response)

asyncio.run(main())
