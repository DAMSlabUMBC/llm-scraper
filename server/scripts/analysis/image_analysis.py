import requests
import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from tqdm import tqdm
import ollama
import re
from analysis.entity_analysis import analyze_text_elements
#from entity_analysis import analyze_text_elements
#import analyze_text_elements

def analyze_image_elements(image_content):
    
    entities = {"entities": set()}
    
    # intializes ollama client
    client = ollama.Client()
    
    # iterates through each image url
    for image_url in tqdm(image_content):
        
        # empties the cache
        torch.cuda.empty_cache()
        
        response = client.chat(
            model='llava:34b', 
            messages=[
#                 {
#                     'role': 'system',
#                     'content': """
#                         You are a Named Entity Recognition (NER) Specialist that extracts IoT-related entities from a given image. The extracted entities must fit into one of these categories:
#                         - devices
#                         - manufacturer
#                         - application
#                         - process
#                         - sensor
#                         - observation
#                         - inference
#                         - research
#                         - privacy policy
#                         - regulation

#                         ### Output Rules:
#                         - Output strictly in the JSON format: `{ "entities": [list of entities] }`
#                         - Do **not** include explanations, reasoning, or extra text.
#                         - Do **not** use the word "json" in the output.
#                         - If no entities are found, return `{ "entities": [] }`.

#                         ### Example Outputs:
#                         **Example 1:**
#                         Input: `"*** Image of an Amazon Echo Dot, With Alexa, Charcoal *** "`
#                         Output:
#                         ```
#                         {
#                             "entities": ["Amazon", "Alexa", "Amazon Echo Dot", "Speaker", "voice assistant"]
#                         }
#                         ```

#                         **Example 2:**
#                         Input: `"*** Image with no IoT entities ***"`
#                         Output:
#                         ```
#                         { "entities": [] }
#                         ```

#                         **INCORRECT OUTPUT:**
#                         ```json
#                         {
#                             "entities": [
#                                 "Smart Soil Moisture Sensor",
#                                 "THIRDREALITY",
#                                 "Zigbee Hub",
#                                 "Alexa Echo Devices",
#                                 "Capacitive Probe",
#                                 "Home Assistant",
#                                 "Hubitat",
#                                 "SmartThings",
#                                 "Homey",
#                                 "Apple Home",
#                                 "Google Home",
#                                 "Remote Monitoring",
#                                 "Automation",
#                                 "OTA Updates",
#                                 "Smart Bridge MZ1"
#                             ]
#                         }
#                         ```

#                         **CORRECT OUTPUT:**
#                         ```
#                         {
#                             "entities": [
#                                 "Smart Soil Moisture Sensor",
#                                 "THIRDREALITY",
#                                 "Zigbee Hub",
#                                 "Alexa Echo Devices",
#                                 "Capacitive Probe",
#                                 "Home Assistant",
#                                 "Hubitat",
#                                 "SmartThings",
#                                 "Homey",
#                                 "Apple Home",
#                                 "Google Home",
#                                 "Remote Monitoring",
#                                 "Automation",
#                                 "OTA Updates",
#                                 "Smart Bridge MZ1"
#                             ]
#                         }
#                         ```


#                         **Remember:** Only return JSON, nothing else.
#                     """,
#                 },
                {
                    'role': 'system',
                    'content': """
                        Provide a detailed description of what you see and can be infered from the given image.
                    """,
                },

                {
                    'role': 'user',
                    'content': image_url,
                },
            ],
            stream=False
        )
        
        print(f"IMAGE DESCRIPTION {response.message.content}")
        
        extracted_entities = analyze_text_elements(response.message.content)
        
        print(f"IMAGE OUTPUT {extracted_entities}")
        
        try:
        
            parsed_json = extract_json(extracted_entities)

            entities_json = eval(parsed_json.strip())

            entities["entities"].update(entities_json["entities"])
        
        except:
            pass
            #print("FAILED TO ADD ENTITIES")
        
        #print(f"ENTITIES {entities}")
    
    entities["entities"] = list(entities["entities"])
        
    return str(entities)

def extract_json(text):
    # Use regex to remove ```json and ``` markers
    return re.sub(r'^```json\n?|```$', '', text, flags=re.MULTILINE).strip()
