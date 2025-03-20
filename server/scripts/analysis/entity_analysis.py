from setup import client
import spacy
import transformers
import ollama
import re
import torch
import json

RETRIES = 3

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
        if isinstance(entities_json, dict):
            if isinstance(entities_json.get("entities"), list):
                if len(entities_json.get("entities")) > 0:
                    if isinstance(entities_json.get("entities")[0], str):
                        break
                else:
                    break

    # entities json has an empty list of entities if it fails to generate entities for a number of retries
    if entities_json == None:
        entities_json = {"entities": []}
    
    return entities_json

def remove_think_tags(text):
    """
    removes think tags from generated deepseek output
    Input: text (with think tags)
    Output: cleaned_text (without think tags)
    """

    # Remove all occurrences of <think>...</think>
    cleaned_text1 = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
    cleaned_text2 = re.sub(r'^.*?</think>', '', text, flags=re.DOTALL).strip()
    
    if len(cleaned_text1) < len(cleaned_text2):
        return cleaned_text1
    else:
        return cleaned_text2
    
def extract_json(text):
    """
    parses out ```json...``` tags if generated by deepseek
    Input: text (potentially with json tags)
    Output: text without json tags
    """
    # Use regex to remove ```json and ``` markers
    return re.sub(r'^```json\n?|```$', '', text, flags=re.MULTILINE).strip()

def extract_python(text):
    """
    parses out ```python...``` tags if generated by deepseek
    Input: text (potentially with python tags)
    Output: text without python tags
    """
    # Use regex to remove ```python and ``` markers
    return re.sub(r'^```python\n?|```$', '', text, flags=re.MULTILINE).strip()