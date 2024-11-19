import requests
import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from tqdm import tqdm

def analyze_image_elements(image_content):

    # Initialize the processor and model
    processor = BlipProcessor.from_pretrained('Salesforce/blip-image-captioning-base')
    model = BlipForConditionalGeneration.from_pretrained('Salesforce/blip-image-captioning-base')

     # Move model to GPU if available
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)

    # Stored the captions generated from the images
    image_caption = ""

    for image_url in tqdm(image_content):
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

            #print(f"Image URL: {image_url}")
            #print(f"Caption: {caption}\n")

            image_caption += caption + '\n'

        except Exception as e:
            print(f"Failed to process image {image_url}: {e}")
    
    return image_caption
