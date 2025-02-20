import threading
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

# Shared variable for working proxy
working_proxy = None
lock = threading.Lock()
PROXIES = []
fake_useragent = UserAgent()

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
        
        # Format proxies properly
        PROXIES = [f"http://{proxy.strip()}" for proxy in proxies if proxy.strip()]
        print(f"[📡] Loaded {len(PROXIES)} proxies.")

    except FileNotFoundError:
        print("[⚠] Proxy file not found. Downloading fresh proxies...")
        download_proxy()
        load_proxies()

def test_proxy(proxy):
    """Checks if a proxy is working by making a test request."""
    global working_proxy
    try:
        print(f"[🛰] Testing Proxy: {proxy}")
        response = requests.get("https://www.example.com", proxies={"http": proxy, "https": proxy}, timeout=5)
        
        if response.status_code == 200:
            with lock:
                if working_proxy is None:  # First working proxy wins
                    working_proxy = proxy
                    print(f"[✅] Working Proxy Found: {proxy}")
    except requests.RequestException:
        pass  # Ignore failed proxy tests

def find_working_proxy():
    """Tests multiple proxies in parallel to find one that works."""
    global working_proxy
    threads = []

    for proxy in PROXIES:
        thread = threading.Thread(target=test_proxy, args=(proxy,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()  # Wait for all threads to finish

    return working_proxy

def local_access(url):
    print("[🌐] Checking URL without proxy")
    try:
        headers = {"User-Agent": fake_useragent.random}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            page_text = response.text.lower()
            if "captcha" in page_text or "verification" in page_text or "verify you are human" in page_text:
                print("[🤖] Bot Protected")
                return False
        elif response.status_code == 403:
            print("[❌] Local access forbidden (403).")
            return False
        elif response.status_code == 503:
            print("[❌] Local access unavailable (503).")
            return False
        elif response.status_code == 429:
            print("[❌] Local access rate limited (429).")
            return False
        elif response.status_code == 404:
            print("[❌] Local access not found (404).")
            return False
        else:
            print(f"[❌] Local access failed with status code: {response.status_code}")
            return False
        
    except requests.RequestException as e:
        print(f"[❌] Error during local access: {e}")
        return False
    
def scrape_website(url):
    """Scrapes a website using a working proxy."""
    global working_proxy    

    ## Load proxies and find a working one
    #load_proxies()
    #proxy = find_working_proxy()
    #
    #if not proxy:
    #    print("[❌] No working proxy found.")
    #    return None
    
    # Check local access first
    if local_access(url):
        print("[✅] Local access successful.")
        return None
    else:
        load_proxies()
        proxy = find_working_proxy()
        
        if not proxy:
            print("[❌] No working proxy found.")
            return None

    # Configure Selenium with the working proxy
    options = Options()
    options.headless = True
    fake_useragent = UserAgent()
    options.add_argument(f'user-agent={fake_useragent.random}')
    options.add_argument(f'--proxy-server={proxy}')
    print(f"[🌐] Scraping with Proxy: {proxy}")

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    html = driver.page_source

    soup = BeautifulSoup(html, 'html.parser')
    driver.quit()

    return soup

# Example Usage
url = "https://www.amazon.com/Smart-Compatible-Assistant-Single-Pole-Certified/dp/B09JZ6W1BH/ref=sr_1_5?dib=eyJ2IjoiMSJ9.YyUdWlFCPDHj7fdR9KXAjgPXxKY87OcP1e_m7O_GJFEFwZx-9FtaiMjDOyIXbbewkED6bSEf7SlAbp97t-qKvpQFN-37BRXh0Ozgi-cM1NeaQXRk5AdWgSWfnmkWGvoWcsIqLUNfNKQO4L0j46Hswx_iySqHCFVmER7JU0h7WApptVAzBQSoP8fBbaZ_BDtSDMnRLE5ZiOg4UejwBKJAuq4U0lC1T8WIBeyJvBiROCZqaTm2Ywm7mEtNxHPj7GDhaOxmNpgddCMnm-wPzYveFbodxJelkM1dx7lV-B3XfdXorasTZ0B560jPfzm5hllKlIs_G8I_vulSNBNw9uecmnVUytn_jRynpXQAPd1p1-x8krhI14LGLYql2NA9X7VSKaZKvlMopcqRNzq6jRCC17c7rvwymbl8TUET056PZi2_sxiBSQdmO81Qrh-UrVZd.YtWOWkxWoG4rQ3k8FFahUql30YHM56CXzxuMtXkoqyg&dib_tag=se&keywords=smart+switches&qid=1737390483&sr=8-5"
scraped_data = scrape_website(url)

if scraped_data:
    print("[✅] Scraping Completed!")
