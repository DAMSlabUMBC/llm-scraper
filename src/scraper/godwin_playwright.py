import asyncio
from playwright.async_api import async_playwright


configurations = {
    "selectors": {
        "title": "#productTitle",
        "integerPartOfPrice": ".a-price-whole", 
        "decimalPartOfPrice": ".a-price-fraction",
        "description": "#feature-bullets ul",
        "images": "#altImages img",
    }
}

async def scrape(configurations, URL):
    async with async_playwright() as pw:
        #loading up the browser and going to it, await making sure we get the actual site rather than a hexidecimal obj
        browser = await pw.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(URL)
        keyFeatures = {}
        
        for keyword in configurations["selectors"]:
            if keyword == "images":
                image_elements = await page.query_selector_all(configurations["selectors"][keyword])
                feature = [await img.get_attribute("src") for img in image_elements]
            
            elif keyword == "description":
                desc_ul = await page.wait_for_selector(configurations["selectors"][keyword])
                li_elements = await desc_ul.query_selector_all("li")
                feature = [await li.inner_text() for li in li_elements]
            
            else:
                featureElement = await page.wait_for_selector(configurations["selectors"][keyword])
                feature = await featureElement.inner_text()

            keyFeatures[keyword] = feature
            
        return keyFeatures
            
        
        
if __name__ == "__main__":
    keyFeatures = asyncio.run(scrape(configurations, "https://www.amazon.com/Amazon-vibrant-helpful-routines-Charcoal/dp/B09B8V1LZ3/ref=sr_1_2?crid=1F7IY81ZKSJRO&dib=eyJ2IjoiMSJ9.NsxhwOLVu_7aGdp5IvUXjabPueDGM6IK7SP92o2AdE3oJJiYRBTp7sLFvGfyLSsHMGv6ugcacFLAPxqAPWIVFNwktjBewbZhAf4pCJF25splBzwYD4MJ0EMY_folPNerTpcmKRElFs456HFF-LhGyp3wnPUyVA37_p2jd9htVk0zqi850eXAFDH_W1ktlKf-xMCQbeP6cGvTfGQAqAkIiN2mISFqBFdNRLdfuMlod4OFhJtk6zjO15pcIYUS8q3iFfSml_9AQJKzOF6-aZuHAOilwUss5xV2OCLeeVR-lPY.yHyQNF2QKNfkG2m7cZeVrzfrVnb4USIktcuH_F5drNQ&dib_tag=se&keywords=alexa&qid=1759091443&s=amazon-devices&sprefix=alex%2Camazon-devices%2C95&sr=1-2&ufe=app_do%3Aamzn1.fos.74097168-0c10-4b8a-b96b-8388a1a12daf&th=1"))
    
    for feature in keyFeatures:
        print(feature, ": ", keyFeatures[feature], '\n')
