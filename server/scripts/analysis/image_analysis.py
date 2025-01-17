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



# from transformers import LlavaNextProcessor, LlavaNextForConditionalGeneration
# import torch
# from PIL import Image
# import requests
# from tqdm import tqdm
# import cloudscraper
# from setup import client
# #import json
# import ast

# def analyze_image_elements(image_content):
#     results = []
    
#     # preprocesses any unrelated images
#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": """
#                                             Clean the list of image urls from any irrelevant logos and sprites.
#                                             Output: [] or [*list of image urls*]
#                             """
#             },
#             {"role": "user", "content": str(image_content)}
#         ]
#     )
#     image_url_list = ast.literal_eval(response.choices[0].message.content)
    
#     # empties the cache
#     torch.cuda.empty_cache()

#     # prepares the model and processor
#     processor = LlavaNextProcessor.from_pretrained("llava-hf/llava-v1.6-mistral-7b-hf")

#     model = LlavaNextForConditionalGeneration.from_pretrained("llava-hf/llava-v1.6-mistral-7b-hf", torch_dtype=torch.float16, low_cpu_mem_usage=True)
#     model.to("cuda:0")

    
#     # analyzes each image
#     for url in tqdm(image_url_list):
#         try:
#             #image = Image.open(scraper.get(url).raw)
#             image = Image.open(requests.get(url, stream=True).raw)

#             conversation = [
#                 {
#                     "role": "user",
#                     "content": [
#                         {"type": "image"},
#                         {"type": "text", "text": "Provide a detailed description of this image."},
#                     ],
#                 },
#             ]
#             prompt = processor.apply_chat_template(conversation, add_generation_prompt=True)
#             inputs = processor(image, prompt, return_tensors="pt").to("cuda:0")

#             # autoregressively complete prompt
#             output = model.generate(**inputs, max_new_tokens=500)

#             result = parse_text(processor.decode(output[0], skip_special_tokens=True))

#             results.append(result)
            
#         except Exception as e:
#             print(f"Failed to process image {url}: {e}")
            
#     return results
        

# def parse_text(input_text, start_tag="[INST]", end_tag="[/INST]"):
#     start_idx = input_text.find(end_tag) + len(end_tag)
#     parsed_text = input_text[start_idx:].strip()
#     return parsed_text
