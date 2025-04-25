from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import os

def get_chrome_driver(headless=True, use_proxy=None):
    """
    Initializes and returns a configured Selenium Chrome WebDriver

    Args:
        headless (bool): Whether to run Chrome in headless mode, default is True
        use_proxy (str or None): Optional proxy server address

    Returns:
        selenium.webdriver.Chrome: A Chrome WebDriver instance with the specified options
    """

    options = Options()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument('--disable-blink-features=AutomationControlled')

    if chrome_path := os.getenv('CHROME_PATH'):
        options.binary_location = chrome_path

    fake_useragent = UserAgent()
    options.add_argument(f'user-agent={fake_useragent.random}')
    
    if use_proxy:
        options.add_argument(f'--proxy-server={use_proxy}')
    
    service = Service(ChromeDriverManager().install())
    
    return webdriver.Chrome(service=service, options=options)
