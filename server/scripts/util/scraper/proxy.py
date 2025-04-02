from modules.amazon import Amazon

import requests
import threading

from fake_useragent import UserAgent
from queue import Queue

MODULES = {"Amazon" : Amazon()}

url = "https://www.amazon.com/Smart-Compatible-Assistant-Single-Pole-Certified/dp/B09JZ6W1BH/ref=sr_1_5?dib=eyJ2IjoiMSJ9.YyUdWlFCPDHj7fdR9KXAjgPXxKY87OcP1e_m7O_GJFEFwZx-9FtaiMjDOyIXbbewkED6bSEf7SlAbp97t-qKvpQFN-37BRXh0Ozgi-cM1NeaQXRk5AdWgSWfnmkWGvoWcsIqLUNfNKQO4L0j46Hswx_iySqHCFVmER7JU0h7WApptVAzBQSoP8fBbaZ_BDtSDMnRLE5ZiOg4UejwBKJAuq4U0lC1T8WIBeyJvBiROCZqaTm2Ywm7mEtNxHPj7GDhaOxmNpgddCMnm-wPzYveFbodxJelkM1dx7lV-B3XfdXorasTZ0B560jPfzm5hllKlIs_G8I_vulSNBNw9uecmnVUytn_jRynpXQAPd1p1-x8krhI14LGLYql2NA9X7VSKaZKvlMopcqRNzq6jRCC17c7rvwymbl8TUET056PZi2_sxiBSQdmO81Qrh-UrVZd.YtWOWkxWoG4rQ3k8FFahUql30YHM56CXzxuMtXkoqyg&dib_tag=se&keywords=smart+switches&qid=1737390483&sr=8-5"

TIME_PATTERN = r"^(?:[0-9]|[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d)?$"
FORBIDDEN_NUMBERS = r"^\d+(\.\d+)?\+?$"
PRICE_PATTERN = r'[\$\€\£\₹]?\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?'
working_proxy = None
thread_lock = threading.Lock()
PROXIES = []
fake_useragent = UserAgent()
failed_proxies = set()

def download_proxy():
    print("Inside of download proxy")
    """
    Fetches free HTTP proxies and saves them to a file
    """

    try:
        # Fetch proxy from HTTP request
        response = requests.get("https://api.proxyscrape.com/v4/free-proxy-list/get?request=get_proxies&protocol=http&proxy_format=ipport&format=text&timeout=10000")
        response.raise_for_status()

        # Write to file
        with open("proxies.txt", "w") as file:
            file.write(response.text.strip())
    except requests.exceptions.RequestException as e:
        print(f"[❌] Error downloading proxies: {e}")
    except IOError as e:
        print(f"[❌] Error writing to file: {e}")

def load_proxy():
    print("Inside of load proxy")
    """
    Reads proxies from the file and formats them for request / Selenium
    """
    global PROXIES
    try:
        # Read from file
        with open("proxies.txt", "r") as file:
            proxies = file.readlines()

        # Format for request
        PROXIES = [f"http://{proxy.strip()}" for proxy in proxies if proxy.strip()]
    except FileNotFoundError:
        print(f"[❌] Error proxy file not found. Downloading fresh proxies...")
    except Exception as e:
        print(f"Error loading proxies: {e}")
        
def find_working_proxy():
    print("Inside of find working proxy")
    """
    Finds a working proxy by testing multiple ones
    """
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
            # TODO: Is this url the one we want to use or a default url to see which proxies work in general
            if test_proxy(proxy,url):
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
