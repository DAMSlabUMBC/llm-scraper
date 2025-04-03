from tqdm import tqdm
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import threading
import logging

from util.scraper.proxy import download_proxy, load_proxy, find_working_proxy, local_access
from util.scraper.browser import get_chrome_driver
from util.server.client import create_sftp_client, ensure_remote_directory
from util.server.server_write import server_write_files

logging.basicConfig(
    filename='html_extractor.log',  # Log file name
    filemode="a",
    level=logging.INFO,             # Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
)

URLS_FILE = "Amazon_product_urls.txt"
GROUP = "amazon"

fake_useragent = UserAgent()

def extract_html(url, html_number, sftp, remote_dest_dir):
    file_name = f"{GROUP}{html_number}.html"
    print(f"[🔍] Scraping url: {url}")

    # Try to access the URL locally first
    if local_access(url):
        print("[✅] Local access successful.")
    else:
        download_proxy()
        load_proxy()
        working_proxy = None
        for i in range(5):
            working_proxy = find_working_proxy()
            if working_proxy is None:
                load_proxy()
            else:
                break
        
        if working_proxy is None:
            print("[❌] No working proxy found.")
            return
        
        print(f"[🛰️] Using working proxy: {working_proxy}")

    # Create Selenium driver with the working proxy
    driver = get_chrome_driver(headless=True, use_proxy=working_proxy)
    try:
        driver.get(url)
        html = driver.page_source

        # Construct the remote file path.
        remote_file_path = os.path.join(remote_dest_dir, file_name)
        print(f"Writing scraped HTML to remote file: {remote_file_path}")

        # Use the helper function to write the HTML to the server
        server_write_files(sftp, remote_file_path, html)
    except Exception as e:
        print(f"Page crash detected for {file_name}, skipping...")
        logging.error(f"Error extracting contents from {GROUP} link {html_number}: {e}")
    finally:
        driver.quit()

if __name__ == '__main__':
    # Server Configuration
    host = os.getenv("HOST_URL")             # Server address
    port = 22                                # Default SFTP port
    username = os.getenv("USERNAME")         # Server username
    password = os.getenv("PASSWORD")         # Server password
    remote_dest_dir = f"/home/{username}/amazon_htmls"
    print(host, username, password, remote_dest_dir)

    # Create the SFTP connection
    sftp, transport = create_sftp_client(host, port, username, password)

    try:
        # Ensure the remote directory exists
        ensure_remote_directory(sftp, remote_dest_dir)

        # Read URLs from the file
        with open(URLS_FILE, "r") as f:
            urls = [url.strip() for url in f.readlines()]

        # Extract HTML for each URL and write to the server
        for i in tqdm(range(len(urls))):
            extract_html(urls[i], i, sftp, remote_dest_dir)
    finally:
        sftp.close()
        transport.close()