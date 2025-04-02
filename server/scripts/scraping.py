from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from util.folder_manager import create_folder
from util.content_saver import save_content, save_links
#from util.media_downloader import ffmpeg_support
import json
import re
import threading
import requests
from queue import Queue
import cloudscraper
from url_extraction.modules.Amazon import Amazon
import time


url = "https://www.amazon.com/Smart-Compatible-Assistant-Single-Pole-Certified/dp/B09JZ6W1BH/ref=sr_1_5?dib=eyJ2IjoiMSJ9.YyUdWlFCPDHj7fdR9KXAjgPXxKY87OcP1e_m7O_GJFEFwZx-9FtaiMjDOyIXbbewkED6bSEf7SlAbp97t-qKvpQFN-37BRXh0Ozgi-cM1NeaQXRk5AdWgSWfnmkWGvoWcsIqLUNfNKQO4L0j46Hswx_iySqHCFVmER7JU0h7WApptVAzBQSoP8fBbaZ_BDtSDMnRLE5ZiOg4UejwBKJAuq4U0lC1T8WIBeyJvBiROCZqaTm2Ywm7mEtNxHPj7GDhaOxmNpgddCMnm-wPzYveFbodxJelkM1dx7lV-B3XfdXorasTZ0B560jPfzm5hllKlIs_G8I_vulSNBNw9uecmnVUytn_jRynpXQAPd1p1-x8krhI14LGLYql2NA9X7VSKaZKvlMopcqRNzq6jRCC17c7rvwymbl8TUET056PZi2_sxiBSQdmO81Qrh-UrVZd.YtWOWkxWoG4rQ3k8FFahUql30YHM56CXzxuMtXkoqyg&dib_tag=se&keywords=smart+switches&qid=1737390483&sr=8-5"

MODULES = {"Amazon": Amazon()}

#PARSE_LIST = ["$", "rating", "review", "recommendation", "deliver", "%", "quantity", "star", "ship", "return"]
TIME_PATTERN = r"^(?:[0-9]|[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d)?$"
FORBIDDEN_NUMBERS = r"^\d+(\.\d+)?\+?$"
PRICE_PATTERN = r'[\$\€\£\₹]?\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?'
working_proxy = None
thread_lock = threading.Lock()
PROXIES = []
fake_useragent = UserAgent()
failed_proxies = set()

def download_proxy():
    """Fetches free HTTP proxies and saves them to a file."""
    try:
        response = requests.get("https://api.proxyscrape.com/v4/free-proxy-list/get?request=get_proxies&protocol=http&proxy_format=ipport&format=text&timeout=10000")
        response.raise_for_status()
        
        with open("proxies.txt", "w") as file:
            file.write(response.text.strip())  # Save proxies
        print("[✅] Proxies downloaded successfully.")

    except requests.exceptions.RequestException as e:
        print(f"[❌] Error downloading proxies: {e}")
    except IOError as e:
        print(f"[❌] Error writing to file: {e}")

def load_proxies():
    """Reads proxies from the file and formats them for requests/Selenium."""
    global PROXIES
    try:
        with open("proxies.txt", "r") as file:
            proxies = file.readlines()
        
        PROXIES = [f"http://{proxy.strip()}" for proxy in proxies if proxy.strip()]
        print(f"[📡] Loaded {len(PROXIES)} proxies.")

    except FileNotFoundError:
        print("[⚠] Proxy file not found. Downloading fresh proxies...")
        download_proxy()
        load_proxies()

def test_proxy(proxy, url):
    """Checks if a proxy works and sets it for future use."""
    global working_proxy
    try:
        print(f"[🌐] Testing Proxy: {proxy}")
        headers = {"User-Agent": fake_useragent.random}
        
        response = requests.get(url, proxies={"http": proxy, "https": proxy}, headers=headers, timeout=10)
        page_text = response.text.lower()

        status_code = {
            403: "forbidden",
            503: "unavailable",
            429: "rate limited",
            404: "not found"
        }
        if response.status_code in status_code:
            print(f"[❌] Proxy {proxy} blocked {status_code[response.status_code]}. Ignoring.")
            failed_proxies.add(proxy)
            return False
        
        for keyword in ["captcha", "verify you are human", "This site can't be reached", "access denied"]:
            if keyword in page_text:
                print(f"[🤖] Proxy {proxy} triggered bot detection. Ignoring. {keyword}")
                failed_proxies.add(proxy)
                return False
        
        if response.status_code == 200:
            with thread_lock:
                if working_proxy is None:
                    working_proxy = proxy
                    print(f"[✅] Found Working Proxy: {proxy}")
                return True

    except requests.RequestException:
        print(f"[❌] Proxy {proxy} failed. Adding to failed list.")
        failed_proxies.add(proxy)
        return False


def find_working_proxy():
    """Finds a working proxy by testing multiple ones."""
    global working_proxy
    proxy_queue = Queue()
    
    for proxy in PROXIES:
        if proxy not in failed_proxies:
            proxy_queue.put(proxy)
    
    threads = []
    
    def worker():
        while not proxy_queue.empty():
            if working_proxy:
                return
            proxy = proxy_queue.get()
            if test_proxy(proxy, url):
                return
            proxy_queue.task_done()
    
    for _ in range(5):  # Change the number of threads to what you want/can handle
        thread = threading.Thread(target=worker)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    return working_proxy

def local_access(url):
    print("[🌐] Checking URL without proxy")
    try:
        headers = {"User-Agent": fake_useragent.random}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            #print(f"RESPONSE {response.text[:500]}")
            #Commenting out the bot detection check for now 
            #fix later
            #page_text = response.text.lower()
            #if "captcha" in page_text or "verification" in page_text or "verify you are human" in page_text:
            #    print("[🤖] Bot Protected")
            #    return False
            return True
        
        status_code = {
            403: "forbidden",
            503: "unavailable",
            429: "rate limited",
            404: "not found"
        }
        if response.status_code in status_code:
            print(f"[❌] {status_code[response.status_code]}")
            return False
        
        print(f"[❌] Local access failed with unexpected status code: {response.status_code}")
        return False
        
    except requests.RequestException as e:
        print(f"[❌] Error during local access: {e}")
        return False

def scrape_website(html, moduleName):
    """
    scrapes the text, image, code, and video content given an html file
    Input:
    html: html code (text)
    moduleName: name of module (site to be scrapped; modules can be defined inside url_extraction/modules)
    Output: 
    text_content: {...} (text)
    image_content: list of image urls
    code_content: [...] (text)
    video_content: (text) 
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


    options = Options()
    options.headless = True
    fake_useragent = UserAgent()
    options.add_argument(f'user-agent={fake_useragent.random}')
    
    if working_proxy:
        options.add_argument(f'--proxy-server={working_proxy}')
    
    options.add_argument("--headless")  # Run headless
    options.add_argument("--no-sandbox")  # Necessary for some restricted environments
    options.add_argument("--disable-dev-shm-usage")  # Overcome resource limitations
        
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    html = driver.page_source"""
    
    # loads the module
    if moduleName in MODULES:
        module = MODULES[moduleName]


    # Fetch the webpage content
    """response = scraper.get(url)
    if response.status_code != 200:
        raise ScrapingError(f"Unable to scrape {url} - Status Code: {response.status_code}")
        #print(f"[❌] Failed to fetch {url}, Status Code: {response.status_code}")
        #return None, None, None, None

    html = response.text"""
    soup = BeautifulSoup(html, 'html.parser')

    # Parse the HTML code with Beautiful Soup
    #soup = BeautifulSoup(html, 'html.parser')
    
    # Create a dynamic folder based on the URL's hostname
    subfolder = create_folder(html)
    
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
            #video_content.append(ffmpeg_support(full_video_url, subfolder['video'], 'video', index=i))
        source = video.find('source')
        for source in video.find_all('source'):
            src = source.get('src')
            if src:
                full_video_url = urljoin(url, src)
                video_links.append(full_video_url)
                #video_content.append(ffmpeg_support(full_video_url, subfolder['video'], 'video', index=i))
    # Filter out any empty transcriptions and join the remaining ones into a single string.
    video_content = " ".join([transcription for transcription in video_content if transcription.strip()])

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
