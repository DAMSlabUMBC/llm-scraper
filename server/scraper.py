import requests
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from openai import OpenAI

load_dotenv()

def scrape_website(url):

    # Retrieve the HTML Content of a Page
    page = requests.get(url)
    
    # Parse the HTML code with Beautiful Soup
    soup = BeautifulSoup(page.content, 'html.parser')

    # Extract text, media, and link elements
    text_elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'p'])

    media_elements = soup.find_all(['img', 'audio', 'video'])

    link_elements = soup.find_all('a')
    
    # Filter and join the text content of important elements
    # Removes leading and trailing whitespace and Ignores HTML tags
    text_content = ' '.join([elem.get_text(strip=True) for elem in text_elements]) 

    # Extract the src attributes of media elements
    media_content = []
    for media in media_elements:
        media_src = media.get('src')
        if media_src:
            media_content.append(media_src)
    # Extract the href attribute of the link elements
    link_content = []
    for link in link_elements:
        link_href = link.get('href')
        if link_href:
            link_content.append(link_href)

    return text_content, media_content, link_content

def analyze_with_llm(combined_content):

    # Pass the HTML content into gpt
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Extract key details such as product name, manufacturer name, product details, and product url from the given content."},
            {"role": "user", "content": combined_content}
        ]
    )
    return response.choices[0].message.content

def main():
    url = "https://www.amazon.com/All-New-release-Smart-speaker-Charcoal/dp/B09B8V1LZ3/ref=pd_ci_mcx_mh_mcx_views_0?pd_rd_w=M1hYW&content-id=amzn1.sym.352fa4e9-2aa8-47c3-b5ac-8a90ddbece20%3Aamzn1.symc.40e6a10e-cbc4-4fa5-81e3-4435ff64d03b&pf_rd_p=352fa4e9-2aa8-47c3-b5ac-8a90ddbece20&pf_rd_r=V0XCAW7K2H716Y192XC5&pd_rd_wg=P6WEm&pd_rd_r=760361b1-d515-438e-bf3d-ede82fbbfce9&pd_rd_i=B09B8V1LZ3"
    
    text_content, media_content, link_content = scrape_website(url)

    combined_content = f"Text: {text_content} \nMedia: {media_content} \nLinks: {link_content}"
    analysis = analyze_with_llm(combined_content)

    print(analysis)

if __name__ == "__main__":
    main()
