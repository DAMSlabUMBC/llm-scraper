import argparse
import os
import json
#import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException
import time
from tqdm import tqdm
from util.scraper.browser import get_chrome_driver

CONFIGS_FOLDER = "config_files"

def scrape_website(url, configs):

    # Setup headless Chrome
    driver = get_chrome_driver()
    driver.get(url)

    text = {}


    print(f"URL {url}")
    for tag in configs["text"]:
        if tag != "buttons":
            try:
                content = None
                if isinstance(configs["text"][tag], list):
                    for name_tag in configs["text"][tag]:
                        try:
                            print(f"Trying selector: {name_tag}")
                            content = driver.find_element(By.CSS_SELECTOR, name_tag).text
                            print(f"Found selector: {name_tag}")
                            break
                        except NoSuchElementException:
                            print(f"Not found selector: {name_tag}")
                            continue
                else:
                    try:
                        content = driver.find_element(By.CSS_SELECTOR, configs["text"][tag]).text
                    except NoSuchElementException:
                        content = None

                if content:
                    text[tag] = "|".join(content.split("\n"))
                else:
                    print(f"No content found for tag: {tag}")

            except Exception as e:
                print(f"Error while processing tag '{tag}': {e}")

    if "buttons" in configs["text"]:
        for button in configs["text"]["buttons"]:
            for xbutton in configs["text"]["buttons"][button]:
                button_selector = xbutton
                content_selector = configs["text"]["buttons"][button][xbutton]
                try:
                    button_element = driver.find_element(By.CSS_SELECTOR, button_selector)
                    driver.execute_script("arguments[0].scrollIntoView(true);", button_element)
                    time.sleep(5)
                    button_element.click()
                    time.sleep(5)  # Optional wait
                    content = driver.find_element(By.CSS_SELECTOR, content_selector).text
                    text[button] = "|".join(content.split("\n"))
                except Exception as e:
                    print(f"Could not click or extract for button '{button}'")

            # reloads the page
            driver.get(url)
            time.sleep(5)
    
    driver.quit()

    return str(text)

        

    