import requests
import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from tqdm import tqdm
import ollama
import re
import io
from analysis.entity_analysis import analyze_text_elements
import base64
import json
#from entity_analysis import analyze_text_elements
#import analyze_text_elements

CLASSIFICATIONS = ["UNRENDERED", "LOGO", "DETAILED"]

RETRIES = 3

def analyze_image_elements(image_content, entity_prompt):
    """
    Extracts image entities
    Input: image_content (list of image urls)
    Output: entities (json of list of entities)
    """
    #classification = ""
    summary = ""
    extracted_entities = ""
    entities = {"entities": set()}
    
    # intializes ollama client
    client = ollama.Client()
    
    # iterates through each image url
    for image_url in tqdm(image_content):

        image = image_url

        classification = ""
        
        # iterates through number of retries to classify an image
        for i in range(RETRIES):

            # empties the cache
            torch.cuda.empty_cache()

            # classifies an image as UNRENDERED, LOGO, and DETAILED
            response = client.chat(
            model='llava:34b',
            messages=[
                {
                    'role': 'system',
                    'content': """
                        You are an AI model designed to classify images into one of three categories: UNRENDERED, LOGO, or DETAILED.

                        **Definitions:**
                        - **UNRENDERED**: The image is blurry, incomplete, pixelated, corrupted, very small, or extremely low-resolution, making it difficult to discern details.
                        - **LOGO**: The image is a simple, symbolic representation, such as a company logo, icon, thumbnail, or watermark, typically with minimal colors, shapes, and no photographic detail.
                        - **DETAILED**: The image contains recognizable objects, scenes, or rich details that can be described, such as photos, artwork, or complex illustrations.

                        **Classification Criteria:**
                        - If the image lacks clarity due to **blurriness, corruption, or extreme pixelation**, classify it as **UNRENDERED**.
                        - If the image is **simple, abstract, or represents a brand symbol**, classify it as **LOGO**.
                        - If the image contains **rich visual details, complex patterns, or multiple identifiable elements**, classify it as **DETAILED**.

                        **Instructions:**
                        - Your response must be **only one of the three labels**: UNRENDERED, LOGO, or DETAILED.
                        - Do **not** provide explanations, descriptions, or additional reasoning.
                        - Output should be in **uppercase** with no additional text.

                        Example Output:
                        ```
                        DETAILED
                        ```

                        ```
                        UNRENDERED
                        ```

                        ```
                        LOGO
                        ```
                    """,
                },
                {
                    'role': 'user',
                    'content': image,
                },
            ],
            stream=False
            )

            classification = response.message.content.upper()

            if classification in CLASSIFICATIONS:
                break
            else:
                classification = ""
        
        # image is automatically UNRENDERED if failed to classify images for number of retries
        if classification not in CLASSIFICATIONS:
            classification = "UNRENDERED"

        print(f"IMAGE CLASSIFICATION: {classification}")

        # summarizes the image if it's DETAILED
        if classification == "DETAILED":

            # summarizes the image
            summary = summarize(image)

            print(f"IMAGE DESCRIPTION {summary}")

            # extracts entities from the image summary
            extracted_entities = analyze_text_elements(summary, entity_prompt)
                
            print(f"IMAGE OUTPUT {extracted_entities}")

            # adds generated entities to the set of image entities
            entities["entities"].update(extracted_entities["entities"])
            
    
    entities["entities"] = list(entities["entities"])
        
    return entities

def summarize(image):
    """
    summarizes a image
    Input: image (url)
    Output: summary (text)
    """

    # intializes ollama client
    client = ollama.Client()

    # empties the cache
    torch.cuda.empty_cache()

    # summarizes the image
    response = client.chat(
            model='llava:34b', 
            messages=[
                {
                    'role': 'system',
                    'content': """
                        Provide a detailed description of what you see and can be infered from the given image.
                    """,
                },

                {
                    'role': 'user',
                    'content': image,
                },
            ],
            stream=False
        )

    summary = response.message.content
    
    return summary
    
