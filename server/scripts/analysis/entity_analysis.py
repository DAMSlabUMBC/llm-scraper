from setup import client
import spacy
import transformers
import ollama
import re
import torch

def analyze_text_elements(text_content):

    # Load English tokenizer, tagger, parser and NER
    # nlp = spacy.load("en_core_web_lg")
    
    # doc = nlp(text_content)

    # spaCy_content = ""

    # # Find named entities, phrases and concepts
    # for entity in doc.ents:
    #     # print(entity.text, entity.label_)
    #     spaCy_content+= entity.text + " "

    # combined_content = f"""
    #     Text: {text_content}
    #     spaCy: {spaCy_content}
    # """
    
    # deepseek-r1:70b
    client = ollama.Client()
    
    # empties the cache
    torch.cuda.empty_cache()

    response = client.chat(
        model='deepseek-r1:70b', 
        messages=[
#             {
#                 'role': 'system',
#                 'content': 
#                 """
#                     You are a Named Entity Recognition (NER) Specialist that will recieve an input of text that has been scraped from a website and a list of 
#                     entities created by spaCy.

#                     You are tasked to do the following:
#                     1. Read the input text carefully.
#                     2. Identify and extract all entities related to IoT devices within the input text. The entities you extract, identify, and return are limited to 
#                     devices, manufacturer, application, process, sensor, observation, inference, research, privacy policy, and regulation. You are allowed to browse the
#                     internet and trained data to identify observations, inferences, reference related research paper, privacy policy, and regulations.
#                     For example:
#                         - devices: cameras, smart speakers, phones, etc.
#                         - manufactureres: Apple, Google, Amazon, etc.
#                         - application: Google Home, Amazon Alexa, Zigbee, Samsung Smartthings, etc.
#                         - process: location tracking, microphone-enabled, activity tracking, etc.
#                         - sensors: microphone, gyroscope, temperature sensor, etc.
#                         - observation: voice assistant
#                         - inference: potential health concerns, ethnicity, gender, age, activity levels, stress levels, etc.
#                         - research: [research paper name]
#                         - privacy policy: Apple Privacy Policy, Samsung Privacy Policy, Alexa Privacy Policy, etc.
#                         - regulation: General Data Protection Regulation (GDPR), California Consumer Privacy Act (CCPA), Personal Information Protection and Electronic Documents Act (PIPEDA), etc.
#                     3. Return them in JSON format, specifically: '{ "entities": [list of entities] }'.
#                     4. If no entities are found, return '{ "entities": [] }'.

#                     Important requirements:
#                     - Do not change, add, or modify any part of the input text Only extract entities that appear in the text or are identified by spaCy.
#                     - Do not output additional explanations or examples beyond the JSON result. End your answer immediately after producing the JSON.
#                     - Do not output the word 'json' in the output
#                     - Here is the expected style:

#                     Example 1:
#                     Input: 'Amazon Echo Dot (newest model), With bigger vibrant sound, helpful routines and Alexa, Charcoal.'
#                     Output: '
#                     {
#                         "entities": [
#                             "Amazon",
#                             "Alexa",
#                             "Amazon Echo Dot",
#                             "Speaker",
#                             "voice assistant",
#                             "location tracking",
#                             "microphone-enabled",
#                             "microphone",
#                             "Alexa Privacy Policy",
#                             "General Data Protection Regulation (GDPR)",
#                             "California Consumer Privacy Act (CCPA)",
#                             "Personal Information Protection and Electronic Documents Act (PIPEDA)",
#                             "speech recognition",
#                             "user behavior analysis",
#                             "potential health concerns",
#                             "background noise detection",
#                             "advertising profiling",
#                             "emotion detection",
#                             "sleep pattern tracking",
#                             "conversation analysis"
#                         ]
#                     }'

#                     Example 2:
#                     Input: 'Govee Smart Light Bulbs, Color Changing Light Bulb, Work with Alexa and Google Assistant, 16 Million Colors RGBWW, WiFi & Bluetooth LED Light Bulbs, Music Sync, A19, 800 Lumens, 4 Pack.'
#                     Output: '
#                     {
#                         "entities": [
#                             "Govee",
#                             "Govee Smart Light Bulbs",
#                             "Light Bulb",
#                             "Alexa",
#                             "Google Assistant",
#                             "RGBWW",
#                             "WiFi",
#                             "Bluetooth",
#                             "LED Light Bulbs",
#                             "A19",
#                             "Alexa Privacy Policy",
#                             "Google Privacy Policy",
#                             "General Data Protection Regulation (GDPR)",
#                             "California Consumer Privacy Act (CCPA)",
#                             "Personal Information Protection and Electronic Documents Act (PIPEDA)",
#                             "voice assistant",
#                             "location tracking",
#                             "activity tracking",
#                             "potential health concerns",
#                             "lighting preferences",
#                             "sleep patterns"
#                         ]
#                     }'

#                     Example 3:
#                     Input: `There are no entities here.`
#                     Output: `{ "entities": [] }`
#                 """,
#             },
            {
                'role': 'system',
                'content': """
                    You are a Named Entity Recognition (NER) Specialist that extracts IoT-related entities from given text. The extracted entities must fit into one of these categories:
                    - devices
                    - manufacturer
                    - application
                    - process
                    - sensor
                    - observation
                    - inference
                    - research
                    - privacy policy
                    - regulation

                    ### Output Rules:
                    - Output strictly in the JSON format: `{ "entities": [list of entities] }`
                    - Do **not** include explanations, reasoning, or extra text.
                    - Do **not** use the word "json" in the output.
                    - If no entities are found, return `{ "entities": [] }`.

                    ### Example Outputs:
                    **Example 1:**
                    Input: `"Amazon Echo Dot, With Alexa, Charcoal."`
                    Output:
                    ```
                    {
                        "entities": ["Amazon", "Alexa", "Amazon Echo Dot", "Speaker", "voice assistant"]
                    }
                    ```

                    **Example 2:**
                    Input: `"There are no entities here."`
                    Output:
                    ```
                    { "entities": [] }
                    ```
                    
                    **INCORRECT OUTPUT:**
                    ```json
                    {
                        "entities": [
                            "Smart Soil Moisture Sensor",
                            "THIRDREALITY",
                            "Zigbee Hub",
                            "Alexa Echo Devices",
                            "Capacitive Probe",
                            "Home Assistant",
                            "Hubitat",
                            "SmartThings",
                            "Homey",
                            "Apple Home",
                            "Google Home",
                            "Remote Monitoring",
                            "Automation",
                            "OTA Updates",
                            "Smart Bridge MZ1"
                        ]
                    }
                    ```
                    
                    **CORRECT OUTPUT:**
                    ```
                    {
                        "entities": [
                            "Smart Soil Moisture Sensor",
                            "THIRDREALITY",
                            "Zigbee Hub",
                            "Alexa Echo Devices",
                            "Capacitive Probe",
                            "Home Assistant",
                            "Hubitat",
                            "SmartThings",
                            "Homey",
                            "Apple Home",
                            "Google Home",
                            "Remote Monitoring",
                            "Automation",
                            "OTA Updates",
                            "Smart Bridge MZ1"
                        ]
                    }
                    ```
                    

                    **Remember:** Only return JSON, nothing else.
                """,
            },

            {
                'role': 'user',
                'content': text_content,
            },
        ],
        stream=False
    )
    
    print(f"before parsing {response.message.content}")
    
    removed_think_tags = remove_think_tags(response.message.content)
    
    removed_json_tags = extract_json(removed_think_tags)
    
    return removed_json_tags

def remove_think_tags(text):
#     """Removes <think>...</think> sections from DeepSeek output."""
#     return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

    # Remove all occurrences of <think>...</think>
    cleaned_text1 = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
    cleaned_text2 = re.sub(r'^.*?</think>', '', text, flags=re.DOTALL).strip()
    
    if len(cleaned_text1) < len(cleaned_text2):
        print('CLEANED TEXT 1')
        return cleaned_text1
    else:
        print('CLEANED TEXT 2')
        return cleaned_text2
    #return cleaned_text.strip()
    
def extract_json(text):
    # Use regex to remove ```json and ``` markers
    return re.sub(r'^```json\n?|```$', '', text, flags=re.MULTILINE).strip()