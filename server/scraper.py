import requests
import os
import ast
import json
import torch
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from openai import OpenAI
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

load_dotenv()

# OpenAI API Key
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def scrape_website(url):

    # Retrieve the HTML Content of a Page
    page = requests.get(url)
    
    # Parse the HTML code with Beautiful Soup
    soup = BeautifulSoup(page.content, 'html.parser')

    # Extract text, media, link, and code elements
    text_elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'p'])

    video_elements = soup.find_all('video')

    audio_elements = soup.find_all('audio')

    image_elements = soup.find_all('img')

    link_elements = soup.find_all('a')
    
    code_elements = soup.find_all('code')

    # Filter and join the text content of important elements
    # Removes leading and trailing whitespace and Ignores HTML tags
    text_content = ' '.join([elem.get_text(strip=True) for elem in text_elements]) 

    # Extract the src attributes of video elements
    video_content = []
    for video in video_elements:
        video_src = video.get('src')
        if video_src:
            video_content.append(video_src)
    
    # Extract the src attributes of video elements
    image_content = []
    for image in image_elements:
        image_src = image.get('src')
        if image_src:
            image_content.append(image_src)
    
    # Extract the src attributes of audio elements
    audio_content = []
    for audio in audio_elements:
        audio_src = audio.get('src')
        if audio_src:
            audio_content.append(audio_src)

    # Extract the href attribute of the link elements
    link_content = []
    for link in link_elements:
        link_href = link.get('href')
        if link_href:
            link_content.append(link_href)

    # Extract and serialize the text content of code elements
    code_content = json.dumps([elem.get_text(strip=True) for elem in code_elements])

    # Return the extracted contents
    return text_content, video_content, image_content, audio_content, link_content, code_content

def new_analyze_with_llm(text, media, links):
    
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

# This function takes in the scraped text elements and analyzes it with an LLM
def analyzeTextElements(text_content):

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Extract key the code and explain to me what it does"},
            {"role": "user", "content": text_content}
        ]
    )
    return response.choices[0].message.content

# This function takes in the scraped media elements and analyzes it with an LLM
def analyzeVideoElements(video_content):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Extract key the code and explain to me what it does"},
            {"role": "user", "content": video_content}
        ]
    )
    return response.choices[0].message.content

# This function takes in the scraped image elements and analyzes it with an LLM
def analyzeImageElements(image_content):

    # Initialize the processor and model
    processor = BlipProcessor.from_pretrained('Salesforce/blip-image-captioning-base')
    model = BlipForConditionalGeneration.from_pretrained('Salesforce/blip-image-captioning-base')


     # Move model to GPU if available
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)

    for image_url in image_content:
        try:
            # Load the image from the URL
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            image = Image.open(response.raw).convert('RGB')

            # Preprocess the image and prepare inputs
            inputs = processor(images=image, return_tensors="pt").to(device)

            # Generate caption
            outputs = model.generate(**inputs)
            caption = processor.decode(outputs[0], skip_special_tokens=True)

            print(f"Image URL: {image_url}")
            print(f"Caption: {caption}\n")

        except Exception as e:
            print(f"Failed to process image {image_url}: {e}")


# This function takes in the scraped audio elements and analyzes it with an LLM
def analyzeAudioElements(audio_content):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Extract key the code and explain to me what it does"},
            {"role": "user", "content": audio_content}
        ]
    )
    return response.choices[0].message.content

# This function takes in the scraped code elements and analyzes it with an LLM
def analyzeCodeElements(code_cotent):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Extract key the code and explain to me what it does"},
            {"role": "user", "content": code_cotent}
        ]
    )
    return response.choices[0].message.content

# This function takes in the result of each LLLM and generates the knowledge graph
def aggregateOutput():
    print("Result")


def main():

    url = "https://www.amazon.com/All-New-release-Smart-speaker-Charcoal/dp/B09B8V1LZ3/ref=pd_ci_mcx_mh_mcx_views_0?pd_rd_w=M1hYW&content-id=amzn1.sym.352fa4e9-2aa8-47c3-b5ac-8a90ddbece20%3Aamzn1.symc.40e6a10e-cbc4-4fa5-81e3-4435ff64d03b&pf_rd_p=352fa4e9-2aa8-47c3-b5ac-8a90ddbece20&pf_rd_r=V0XCAW7K2H716Y192XC5&pd_rd_wg=P6WEm&pd_rd_r=760361b1-d515-438e-bf3d-ede82fbbfce9&pd_rd_i=B09B8V1LZ3"
    urlCodeTest = "https://mui.com/material-ui/react-modal/"
    
    text_content, video_content, image_content, audio_content, link_content, code_content = scrape_website(url)

    textResult = analyzeTextElements(text_content)

    videoResult = analyzeVideoElements(video_content)

    imageResult = analyzeImageElements(image_content)

    audioResult = analyzeAudioElements(audio_content)

    codeResult = analyzeCodeElements(code_content)

    print(imageResult)

if __name__ == "__main__":
    main()
