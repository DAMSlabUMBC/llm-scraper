import os
from bs4 import BeautifulSoup

def create_folder(driver):
    #create a general folder
    product_name = extract_product_name(driver)
    base_folder = os.path.join(os.getcwd(), product_name)
    os.makedirs(base_folder, exist_ok=True)
    
    # Create subfolders
    content_types = ['video', 'audio']
    subfolders = {content_type: os.path.join(base_folder, content_type) for content_type in content_types}
    for folder in subfolders.values():
        os.makedirs(folder, exist_ok=True)
    return subfolders

def extract_product_name(driver):
    try:
        #soup = BeautifulSoup(driver.page_source, 'html.parser')
        soup = BeautifulSoup(driver.text, 'html.parser')
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
