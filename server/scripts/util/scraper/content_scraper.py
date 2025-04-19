from util.scraper.browser import get_chrome_driver
from util.scraper.proxy import working_proxy, local_access, url, MODULES

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

import json

def scrape_website(html, moduleName):
    """
    Scrapes structured content (text, images, code snippets, and videos) from a webpage.

    Args:
        html (string): The HTML of the webpage to scrape.
        module_name (string): The name of the parsing module to use. Each module is expected to 
                           define a `parseProducts(soup)` function for extracting relevant content.

    Returns:
        dict: A dictionary containing extracted content with the following keys:
            - "text": Parsed text content (typically product descriptions or article body).
            - "images": List of image URLs found on the page.
            - "code": JSON-encoded list of code snippets found within <code> tags.
            - "videos": List of video URLs extracted from <video> and <source> tags.
    """

    module = None
    global working_proxy

    # Local: use proxy rotation and selenium webdriver configuration to store html files locally to scrape entities    
    """if local_access(url):
        print("[✅] Local access successful.")
    else:
        download_proxy()
        load_proxies()
        working_proxy = find_working_proxy()
        if working_proxy is None:
            load_proxies()
            working_proxy = find_working_proxy()
        if working_proxy is None:
            print("[❌] No working proxy found.")
            return None
        
        print(f"[🛰️] Using working proxy: {working_proxy}")

    # Selenium WebDriver Configuration
    """

    driver = get_chrome_driver()
    driver.get(url)
    html = driver.page_source
    # loads the module
    if moduleName in MODULES:
        module = MODULES[moduleName]

    soup = BeautifulSoup(html, 'html.parser')

    # Parse the HTML code with Beautiful Soup
    #soup = BeautifulSoup(html, 'html.parser')
    
    
    # Extract and text content based on given module
    print('[✅] Extracting Text')
    text_content = module.parseProducts(soup)

    # Extract and serialize the text content of code elements
    print('[✅] Extracting Code')
    code_elements = soup.find_all('code')
    code_content = json.dumps([elem.get_text(strip=True) for elem in code_elements])

    # Extract the src attributes of video elements
    print('[✅] Extracting Images')
    image_elements = soup.find_all('img')
    image_content = []
    for image in image_elements:
        image_src = image.get('src')
        if image_src:
            image_content.append(image_src)
        source = image.find('source')
        for source in image.find_all('source'):
            src = source.get('src')
            if src:
                image_content.append(src)

    # Extract and download the video links
    print('[✅] Extracting Video')
    video_elements = soup.find_all('video')
    video_links = []
    video_content = []

    for i, video in enumerate(video_elements):
        src = video.get('src')
        if src:
            full_video_url = urljoin(url, src)
            video_links.append(full_video_url)
        source = video.find('source')
        for source in video.find_all('source'):
            src = source.get('src')
            if src:
                full_video_url = urljoin(url, src)
                video_links.append(full_video_url)
    # Filter out any empty transcriptions and join the remaining ones into a single string.
    video_content = " ".join([transcription for transcription in video_content if transcription.strip()])

    print('[💆‍♂️] Video Content Baby: ', video_content)

    return text_content, image_content, code_content, video_content


