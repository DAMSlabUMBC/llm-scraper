import requests
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from openai import OpenAI

load_dotenv()

def scrape_website(url):

    #Scrape HTML Conten from a page
    page = requests.get(url)
    
    # Parse the HTML code with Beautiful Soup
    soup = BeautifulSoup(page.content, 'html.parser')

    # Extract important elements
    important_elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'title', 'p', 'meta'])
    
    # Filter and join the text content of important elements
    # Removes leading and trailing whitespace + Ignores HTML tags
    filtered_content = ' '.join([elem.get_text(strip=True) for elem in important_elements]) 

    return filtered_content

def analyze_with_llm(content):

    # Pass the HTML content into gpt
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert with product information. Extract key details such as product name, description, price, and features from the given content."},
            {"role": "user", "content": content}
        ]
    )
    return response.choices[0].message.content

def main():
    url = "https://www.amazon.com/All-New-release-Smart-speaker-Charcoal/dp/B09B8V1LZ3/ref=pd_ci_mcx_mh_mcx_views_0?pd_rd_w=M1hYW&content-id=amzn1.sym.352fa4e9-2aa8-47c3-b5ac-8a90ddbece20%3Aamzn1.symc.40e6a10e-cbc4-4fa5-81e3-4435ff64d03b&pf_rd_p=352fa4e9-2aa8-47c3-b5ac-8a90ddbece20&pf_rd_r=V0XCAW7K2H716Y192XC5&pd_rd_wg=P6WEm&pd_rd_r=760361b1-d515-438e-bf3d-ede82fbbfce9&pd_rd_i=B09B8V1LZ3"
    
    filtered_content = scrape_website(url)
    analysis = analyze_with_llm(filtered_content)

    print(analysis)

if __name__ == "__main__":
    main()