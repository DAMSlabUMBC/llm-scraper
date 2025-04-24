import ollama
import torch
import json
from util.llm_utils.response_cleaner import extract_json, extract_python, remove_think_tags
import re

RETRIES = 3

ENTITIES_PATTERN = r"^\{'entities': \[(?:'(?:[^']*)'(?:, )?)*\]\}$"

def analyze_text_elements(text_content):
    entities_json = {"entities": []}

    # initializes ollama client
    client = ollama.Client()

    # generates entities for number of retries
    for i in range(RETRIES):
    
        # empties the cache
        torch.cuda.empty_cache()

        # generates entities given some text_content
        response = client.chat(
            model='deepseek-r1:70b', 
            messages=[
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
                        - category

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
        
        removed_json_tags = extract_json(extract_python(removed_think_tags))

        # checks if the generated output is a json
        try:
            entities_json = json.loads(removed_json_tags.strip())
        except json.JSONDecodeError as e:
            entities_json = None

        # checks if it in the desired format {'entities': [...]}
        """if isinstance(entities_json, dict):
            if isinstance(entities_json.get("entities"), list):
                if len(entities_json.get("entities")) > 0:
                    if isinstance(entities_json.get("entities")[0], str):
                        break
                else:
                    break"""
        if re.match(ENTITIES_PATTERN, entities_json):
            break
        else:
            entities_json = None
            
    # entities json has an empty list of entities if it fails to generate entities for a number of retries
    if entities_json == None:
        entities_json = {"entities": []}
    
    return entities_json
