from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from util.folder_manager import create_folder
from util.content_saver import save_content, save_links
from util.media_downloader import ffmpeg_support
import json

def scrape_website(url):

    # Selenium WebDriver Configuration
    options = Options()
    options.headless = True
    fake_useragent = UserAgent()
    options.add_argument(f'user-agent={fake_useragent.random}')
    
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    html = driver.page_source

    # Parse the HTML code with Beautiful Soup
    soup = BeautifulSoup(html, 'html.parser')
    
    # Create a dynamic folder based on the URL's hostname
    subfolder = create_folder(driver)
    
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