from bs4 import BeautifulSoup
import requests
import json

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

    # Join text content
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
