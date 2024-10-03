import requests
import os
import ast
import json
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from openai import OpenAI
from PIL import Image

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

def new_analyze_with_llm(text, media, links):
    
    # Pass the HTML content into gpt
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    media_content = f"Media {media}"


    print("OLD MEDIA CONTENT")
    print(media_content)
    print(len(media))
    print()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Clean the list of image urls from any irrelevant logos and sprites. Output: a list of image urls"},
            {"role": "user", "content": media_content}
        ]
    )

    str_output = response.choices[0].message.content

    print("ANALYSIS")
    print("Total tokens", response.usage.total_tokens)
    print("Prompt tokens", response.usage.prompt_tokens)
    print("Completion tokens", response.usage.completion_tokens)

    print("NEW MEDIA CONTENT")
    start = str_output.find("[")
    end = str_output.find("]")

    str_list = str_output[start:end+1]

    image_urls = ast.literal_eval(str_list)

    print(image_urls)
    print(type(image_urls))
    print(len(image_urls))

    short_image_urls = image_urls[5:8]

    for image in short_image_urls:

        response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Here is a screenshot to an image. Perform the following steps: 1. Extract any IoT-related entities from the image. 2. With the generated entities and the screenshot, produce a set of triplets with the given information. Triplet: (entity, relationship, entity). 3. Reduce the entities in the triplets to 1-3 words. 4. Reduce the relationships in the triplets to 1 word. If unable to analyze the image, return \"unprocessed\" Output: a set of triplets or \"unprocessed\"."},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image,
                                    "detail": "low",
                                }
                            }
                        ]
                    }
                ]
            )
    
        print(response.choices[0].message.content)

        print("ANALYSIS")
        print("Total tokens", response.usage.total_tokens)
        print("Prompt tokens", response.usage.prompt_tokens)
        print("Completion tokens", response.usage.completion_tokens)

    
def main():
    url = "https://www.amazon.com/All-New-release-Smart-speaker-Charcoal/dp/B09B8V1LZ3/ref=pd_ci_mcx_mh_mcx_views_0?pd_rd_w=M1hYW&content-id=amzn1.sym.352fa4e9-2aa8-47c3-b5ac-8a90ddbece20%3Aamzn1.symc.40e6a10e-cbc4-4fa5-81e3-4435ff64d03b&pf_rd_p=352fa4e9-2aa8-47c3-b5ac-8a90ddbece20&pf_rd_r=V0XCAW7K2H716Y192XC5&pd_rd_wg=P6WEm&pd_rd_r=760361b1-d515-438e-bf3d-ede82fbbfce9&pd_rd_i=B09B8V1LZ3"
    
    text_content, media_content, link_content = scrape_website(url)

    combined_content = f"Text: {text_content} \nMedia: {media_content} \nLinks: {link_content}"
    """print("combined content")
    print(combined_content)
    print(type(combined_content))"""

    """media_content = f"Media {media_content}"
    print(media_content)
    print(type(media_content))"""

    """print("TEXT CONTENT")
    print(text_content)
    print()"""

    """print("MEDIA CONTENT")
    print(media_content)
    print()"""

    """print("LINK CONTENT")
    print(link_content)
    print()"""
    #analysis = analyze_with_llm(combined_content)

    new_analyze_with_llm(text_content, media_content, link_content)

    #new_analysis = new_analyze_with_llm(text_content, media_content, link_content)

    #print(new_analysis)

    #print(analysis)

if __name__ == "__main__":
    main()
