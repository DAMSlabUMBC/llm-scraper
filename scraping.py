from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse, unquote
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import os
import base64
import time
import subprocess
import undetected_chromedriver as uc

# Creating The Fodler
def create_folder(driver):
    #create a general folder
    product_name = extract_product_name(driver)
    base_folder = os.path.join(os.getcwd(), product_name)
    os.makedirs(base_folder, exist_ok=True)
    
    # Create subfolders
    content_types = ['text', 'video', 'audio', 'image', 'links', 'code', 'page']
    subfolders = {content_type: os.path.join(base_folder, content_type) for content_type in content_types}
    for folder in subfolders.values():
        os.makedirs(folder, exist_ok=True)
    return subfolders

# Extracting Product Name
def extract_product_name(driver):
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # grabing the h1
        product_name = soup.find('h1')
        if product_name:
            return ''.join(c if c.isalnum() else '_' for c in product_name.get_text(strip=True))
        # if we cant grab the h1 we go to the <title> tag
        title_tag = soup.find('title')
        if title_tag:
            return ''.join(c if c.isalnum() else '_' for c in title_tag.get_text(strip=True))
    except Exception as e:
        print(f"[🛑] Error extracting product name: {e}")
    return None 

# determine the type of media source
def save_content(subfolders, content, content_type, extension="txt"):
    folder = subfolders[content_type]
    file_path = os.path.join(folder, f"{content_type}_content.{extension}")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

# Save links to a specified file in the links folder
def save_links(folder, links, filename):
    """Save links to a specified file in the links folder."""
    file_path = os.path.join(folder, filename)
    with open(file_path, 'w') as f:
        for link in links:
            f.write(f"{link}\n")

def normal_scraper(url):
    # Configure Selenium WebDriver
    options = Options()
    options.headless = True
    fake_useragent = UserAgent()
    options.add_argument(f'user-agent={fake_useragent.random}')
    
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    # Create a dynamic folder based on the URL's hostname
    subfolder = create_folder(driver)
    
    # From Kent    
    # Extract text, media, link, and code elements
    print(f"[✅] Extracting URL")
    text_elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'p'])
    text_content = ' '.join([elem.get_text(strip=True) for elem in text_elements])
    save_content(subfolder, text_content, 'text', extension="txt")

    code_elements = soup.find_all('code')
    code_content = ' '.join([elem.get_text(strip=True) for elem in code_elements])
    save_content(subfolder, code_content, 'code', extension="txt")
    
    video_elements = soup.find_all('video')
    audio_elements = soup.find_all('audio')
    image_elements = soup.find_all('img')
    link_elements = soup.find_all('a')

    
    print(f"[✅] Extracting Page")
    layout_content = soup.prettify()
    save_content(subfolder, layout_content, 'page', extension="html")
    
    # Initialize link lists
    a_links = []
    video_links = []
    image_links = []
    code_links = []
    
    # Collect and process video links
    for i, video in enumerate(video_elements):
        src = video.get('src')
        if src:
            full_video_url = urljoin(url, src)
            video_links.append(full_video_url)
            ffmpeg_support(full_video_url, subfolder['video'], 'video', index=i)
        source = video.find('source')
        for source in video.find_all('source'):
            src = source.get('src')
            if src:
                full_video_url = urljoin(url, src)
                video_links.append(full_video_url)
                ffmpeg_support(full_video_url, subfolder['video'], 'video', index=i)
        # still need to be tested
        #iframe_element = soup.find_all('iframe')
        #for iframe in iframe_element:
        #    src = iframe.get('src')
        #    if src:
        #        full_video_url = urljoin(url, src)
        #        video_links.append(full_video_url)
        #        ffmpeg_support(full_video_url, subfolder['video'], 'video', index=i)
                
    # Collect and process image links
    for i, image in enumerate(image_elements):
        src = image.get('src')
        if src:
            full_image_url = urljoin(url, src)
            extension = os.path.splitext(full_image_url)[1].lstrip('.') or 'jpg'
            image_links.append(full_image_url)
            image_download(full_image_url, subfolder['image'], 'image', index=i, extension=extension)
            
    # Collect <a> tag links
    for link in link_elements:
        href = link.get('href')
        if href:
            full_link_url = urljoin(url, href)
            a_links.append(full_link_url)
            
    # Collect and download JavaScript files
    script_elements = soup.find_all('script')
    for i, script in enumerate(script_elements):
        src = script.get('src')
        if src:
            full_js_url = urljoin(url, src)
            code_links.append(full_js_url)
            js_download(full_js_url, subfolder['code'])
    
    # Save all collected links in the links folder
    save_links(subfolder['links'], a_links, "a_links.txt")
    save_links(subfolder['links'], video_links, "video_links.txt")
    save_links(subfolder['links'], image_links, "image_links.txt")


#https://www.ffmpeg.org/documentation.html
def ffmpeg_support(url, folder, media_type, index, extension="mp4"):
    output_filename = os.path.join(folder, f"{media_type}_{index}.{extension}")
    try:
        if url.startswith("data:"):
            # Handle data URL
            header, encoded = url.split(",", 1)
            mime_type = header.split(":")[1].split(";")[0]
            extension = mime_type.split("/")[-1]
            decoded_data = base64.b64decode(encoded)
            
            # Save decoded data to a temporary file
            temp_filename = os.path.join(folder, f"temp_{index}.{extension}")
            with open(temp_filename, "wb") as f:
                f.write(decoded_data)

            # Convert and save final output with FFmpeg
            ffmpeg_command = ["ffmpeg", "-i", temp_filename, output_filename]
            subprocess.run(ffmpeg_command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Remove temporary file
            os.remove(temp_filename)
            print(f"[✅] Video Downloaded {output_filename}")

        else:
            # Handle standard media URL
            ffmpeg_command = ["ffmpeg", "-i", url, output_filename]
            subprocess.run(ffmpeg_command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"[✅] Saved {media_type}_{index} to {output_filename}")
    except subprocess.CalledProcessError as e:
        print(f"[🛑] FFmpeg failed {media_type}: {e}")
    except Exception as e:
        print(f"[🛑] Failed {media_type} URL with FFmpeg: {e}")
        
def image_download(url, folder, media_type, index, extension="jpg"):
    output_filename = os.path.join(folder, f"{media_type}_{index}.{extension}")
    try:
        if url.startswith("data:"):
            # Handle data URL
            header, encoded = url.split(",", 1)
            mime_type = header.split(":")[1].split(";")[0]
            extension = mime_type.split("/")[-1]
            decoded_data = base64.b64decode(encoded)
            with open(output_filename, "wb") as f:
                f.write(decoded_data)
            print(f"[✅] Successfully download Image {output_filename}")
        else:
            # Handle standard media URL
            response = requests.get(url)
            response.raise_for_status()
            with open(output_filename, "wb") as f:
                f.write(response.content)
            print(f"[✅] {media_type} Downloaded {output_filename}")
    except requests.RequestException as e:
        print(f"[🛑] Failed to download {media_type}_{index} URL: {e}")
    except Exception as e:
        print(f"[🛑] Failed to grab {media_type}_{index} URL: {e}")
    
def js_download(url, folder):
    name = os.path.basename(url)
    output_filename = os.path.join(folder, f"{name}.js")
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(output_filename, "w") as f:
            f.write(response.text)
        print(f"[✅] Downloaded JavaScript from URL to {output_filename}")
    except requests.RequestException as e:
        print(f"[🛑] Failed to download JavaScript from URL: {e}")
    except Exception as e:
        print(f"[🛑] Failed to grab JavaScript URL: {e}")



# testing hahah stuff
#def undetected_browser_scrape(url):
#    # Configure undetected Chrome WebDriver
#    options = uc.ChromeOptions()
#    options.headless = False
#    UserAgent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
#    options.add_argument(f'user-agent={UserAgent}')
#    driver = uc.Chrome(options=options)
#    
#    driver.get(url)
#    time.sleep(3)
#    
#    html = driver.page_source
#    soup = BeautifulSoup(html, 'html.parser')
#    
#    # Create a dynamic folder based on the URL's hostname
#    base_folder, subfolder = create_folder(url, driver)
#    
#    # From Kent    
#    # Extract text, media, link, and code elements
#    print(f"[✅] Extracting URL")
#    text_elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'p'])
#    text_content = ' '.join([elem.get_text(strip=True) for elem in text_elements])
#    save_content(subfolder, text_content, 'text', extension="txt")
#
#    code_elements = soup.find_all('code')
#    code_content = ' '.join([elem.get_text(strip=True) for elem in code_elements])
#    save_content(subfolder, code_content, 'code', extension="txt")
#    
#    video_elements = soup.find_all('video')
#    audio_elements = soup.find_all('audio')
#    image_elements = soup.find_all('img')
#    link_elements = soup.find_all('a')
#
#    
#    print(f"[✅] Extracting Page")
#    layout_content = soup.prettify()
#    save_content(subfolder, layout_content, 'page', extension="html")
#    
#    # Initialize link lists
#    a_links = []
#    video_links = []
#    image_links = []
#    code_links = []
#    
#    # Collect and process video links
#    for i, video in enumerate(video_elements):
#        src = video.get('src')
#        if src:
#            full_video_url = urljoin(url, src)
#            video_links.append(full_video_url)
#            ffmpeg_support(full_video_url, subfolder['video'], 'video', index=i)
#        source = video.find('source')
#        for source in video.find_all('source'):
#            src = source.get('src')
#            if src:
#                full_video_url = urljoin(url, src)
#                video_links.append(full_video_url)
#                ffmpeg_support(full_video_url, subfolder['video'], 'video', index=i)
#        # still need to be tested
#        #iframe_element = soup.find_all('iframe')
#        #for iframe in iframe_element:
#        #    src = iframe.get('src')
#        #    if src:
#        #        full_video_url = urljoin(url, src)
#        #        video_links.append(full_video_url)
#        #        ffmpeg_support(full_video_url, subfolder['video'], 'video', index=i)
#        
#                
#    # Collect and process image links
#    for i, image in enumerate(image_elements):
#        src = image.get('src')
#        if src:
#            full_image_url = urljoin(url, src)
#            extension = '.jpg'
#            image_links.append(full_image_url)
#            image_download(full_image_url, subfolder['image'], 'image', index=i, extension=extension)
#            
#    # Collect <a> tag links
#    for link in link_elements:
#        href = link.get('href')
#        if href:
#            full_link_url = urljoin(url, href)
#            a_links.append(full_link_url)
#            
#    # Collect and download JavaScript files
#    script_elements = soup.find_all('script')
#    for i, script in enumerate(script_elements):
#        src = script.get('src')
#        if src:
#            full_js_url = urljoin(url, src)
#            code_links.append(full_js_url)
#            js_download(full_js_url, subfolder['code'])
#    
#    # Save all collected links in the links folder
#    save_links(subfolder['links'], a_links, "a_links.txt")
#    save_links(subfolder['links'], video_links, "video_links.txt")
#    save_links(subfolder['links'], image_links, "image_links.txt")
    
def everything(url):
    normal_scraper(url)
    #undetected_browser_scrape(url)
    
    