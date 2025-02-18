from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from util.folder_manager import create_folder
from util.content_saver import save_content, save_links
from util.media_downloader import ffmpeg_support
import json
import re
import cloudscraper
from errors import ScrappingError

#PARSE_LIST = ["$", "rating", "review", "recommendation", "deliver", "%", "quantity", "star", "ship", "return"]
TIME_PATTERN = r"^(?:[0-9]|[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d)?$"
FORBIDDEN_NUMBERS = r"^\d+(\.\d+)?\+?$"
PRICE_PATTERN = r'[\$\€\£\₹]?\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?'

def scrape_website(url):

    # Selenium WebDriver Configuration
    """options = Options()
    options.headless = True
    fake_useragent = UserAgent()
    options.add_argument(f'user-agent={fake_useragent.random}')
    options.add_argument("--headless")  # Run headless
    options.add_argument("--no-sandbox")  # Necessary for some restricted environments
    options.add_argument("--disable-dev-shm-usage")  # Overcome resource limitations
        
    driver = webdriver.Chrome(options=options)
    driver.get(url)"""
    
    # Create a cloudscraper instance
    scraper = cloudscraper.create_scraper()

    # Fetch the webpage content
    response = scraper.get(url)
    if response.status_code != 200:
        raise ScrapingError(f"Unable to scrape {url} - Status Code: {response.status_code}")
        #print(f"[❌] Failed to fetch {url}, Status Code: {response.status_code}")
        #return None, None, None, None

    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    # Parse the HTML code with Beautiful Soup
    #soup = BeautifulSoup(html, 'html.parser')
    
    # Create a dynamic folder based on the URL's hostname
    subfolder = create_folder(response)
    
    # Extract and join the text content
    print('[✅] Extracting Text')
    text_elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'p'])
    text_content = ' '.join([elem.get_text(strip=True) for elem in text_elements])

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
            video_content.append(ffmpeg_support(full_video_url, subfolder['video'], 'video', index=i))
        source = video.find('source')
        for source in video.find_all('source'):
            src = source.get('src')
            if src:
                full_video_url = urljoin(url, src)
                video_links.append(full_video_url)
                video_content.append(ffmpeg_support(full_video_url, subfolder['video'], 'video', index=i))

    print('[💆‍♂️] Video Content Baby: ', video_content)

    return text_content, image_content, code_content, video_content

def preprocess(text_content):
    parsed_lines = []
    clean_lines = []
    no_duplicates = []

    # removing the duplicates
    for line in text_content.split("\n"):
        no_duplicates.append(line.strip())

    no_duplicates = list(set(no_duplicates))

    for line in no_duplicates:
        new_line = []
        for word in line.split():

            """if not bool(re.match(PRICE_PATTERN, word)):
                new_line.append(word)"""

            # removes prices and percentages
            if not word.startswith("$") and not word.endswith("%") and not bool(re.match(TIME_PATTERN, word)):
                new_line.append(word)

        parsed_lines.append(" ".join(new_line))

    for line in parsed_lines:
        
        # parsed out any lines with less than or equal to 2 words
        if len(line.split()) > 2:
            clean_lines.append(line)
    
    return "\n".join(clean_lines)


def numTokens(text_content):
    num_tokens = 0

    for line in text_content.split("\n"):
        num_tokens += len(line)
    
    return num_tokens
