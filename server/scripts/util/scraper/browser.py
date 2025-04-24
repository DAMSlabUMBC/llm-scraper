from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
#import chromedriver_binary
from selenium.webdriver.chrome.service import Service
import os
import chromedriver_autoinstaller
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

PATH = "/umbc/ada/ryus/users/gsantos2/tools/chromedriver"


def get_chrome_driver(headless=True, use_proxy=None):
    """
    Initializes and returns a configured Selenium Chrome WebDriver

    Args:
        headless (bool): Whether to run Chrome in headless mode, default is True
        use_proxy (str or None): Optional proxy server address

    Returns:
        selenium.webdriver.Chrome: A Chrome WebDriver instance with the specified options
    """

    #chromedriver_autoinstaller.install()

    # Choose a custom install path OUTSIDE your home directory
    # driver_dir = PATH
    # os.makedirs(driver_dir, exist_ok=True)

    # # Installs ChromeDriver that matches your Chrome version
    # chromedriver_autoinstaller.install(path=driver_dir)

    # # Use that path explicitly
    # chromedriver_path = os.path.join(driver_dir, "chromedriver")

    options = Options()
    if headless:
        options.add_argument("--headless=new")
    else:
        options.headless=False
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")
    # options.add_argument('--disable-blink-features=AutomationControlled')

    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    #options.add_argument("--window-size=1920,1080")

    # if chrome_path := os.getenv('CHROME_PATH'):
    #     options.binary_location = chrome_path

    # fake_useragent = UserAgent()
    # options.add_argument(f'user-agent={fake_useragent.random}')
    
    # if use_proxy:
    #     options.add_argument(f'--proxy-server={use_proxy}')
    
    return webdriver.Chrome(options=options)