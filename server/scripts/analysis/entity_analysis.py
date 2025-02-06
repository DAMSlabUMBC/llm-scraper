from setup import client
import spacy
import transformers

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

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": 
            """

                You are a Named Entity Recognition (NER) Specialist that will recieve an input of text that has been scraped from a website and a list of 
                entities created by spaCy.

                You are tasked to do the following:
                1. Identify and extract all entities related to IoT devices within the input text. The entities you extract, identify, and return are limited to 
                devices, manufacturer, application, process, sensor, observation, inference, research, privacy policy, and regulation. You are allowed to browse the
                internet and trained data to identify observations, inferences, reference related research paper, privacy policy, and regulations.
                For example:
                    - devices: cameras, smart speakers, phones, etc.
                    - manufactureres: Apple, Google, Amazon, etc.
                    - application: Google Home, Amazon Alexa, Zigbee, Samsung Smartthings, etc.
                    - process: location tracking, microphone-enabled, activity tracking, etc.
                    - sensors: microphone, gyroscope, temperature sensor, etc.
                    - observation: voice assistant
                    - inference: potential health concerns, ethnicity, gender, age, activity levels, stress levels, etc.
                    - research: [research paper name]
                    - privacy policy: Apple Privacy Policy, Samsung Privacy Policy, Alexa Privacy Policy, etc.
                    - regulation: General Data Protection Regulation (GDPR), California Consumer Privacy Act (CCPA), Personal Information Protection and Electronic Documents Act (PIPEDA), etc.
                2. Return them in JSON format, specifically: '{ "entities": [list of entities] }'.
                3. If no entities are found, return '{ "entities": [] }'.

                Important requirements:
                - Do not change, add, or modify any part of the input text Only extract entities that appear in the text or are identified by spaCy.
                - Do not output additional explanations or examples beyond the JSON result. End your answer immediately after producing the JSON.
                - Do not output the word 'json' in the output
                - Here is the expected style:

                Example 1:
                Input: 'Amazon Echo Dot (newest model), With bigger vibrant sound, helpful routines and Alexa, Charcoal.'
                Output: '
                {
                    "entities": [
                        "Amazon",
                        "Alexa",
                        "Amazon Echo Dot",
                        "Speaker",
                        "voice assistant",
                        "location tracking",
                        "microphone-enabled",
                        "microphone",
                        "Alexa Privacy Policy",
                        "General Data Protection Regulation (GDPR)",
                        "California Consumer Privacy Act (CCPA)",
                        "Personal Information Protection and Electronic Documents Act (PIPEDA)",
                        "speech recognition",
                        "user behavior analysis",
                        "potential health concerns",
                        "background noise detection",
                        "advertising profiling",
                        "emotion detection",
                        "sleep pattern tracking",
                        "conversation analysis"
                    ]
                }'

                Example 2:
                Input: 'Govee Smart Light Bulbs, Color Changing Light Bulb, Work with Alexa and Google Assistant, 16 Million Colors RGBWW, WiFi & Bluetooth LED Light Bulbs, Music Sync, A19, 800 Lumens, 4 Pack.'
                Output: '
                {
                    "entities": [
                        "Govee",
                        "Govee Smart Light Bulbs",
                        "Light Bulb",
                        "Alexa",
                        "Google Assistant",
                        "RGBWW",
                        "WiFi",
                        "Bluetooth",
                        "LED Light Bulbs",
                        "A19",
                        "Alexa Privacy Policy",
                        "Google Privacy Policy",
                        "General Data Protection Regulation (GDPR)",
                        "California Consumer Privacy Act (CCPA)",
                        "Personal Information Protection and Electronic Documents Act (PIPEDA)",
                        "voice assistant",
                        "location tracking",
                        "activity tracking",
                        "potential health concerns",
                        "lighting preferences",
                        "sleep patterns"
                    ]
                }'

                Example 3:
                Input: `There are no entities here.`
                Output: `{ "entities": [] }`


            """
            },
            {"role": "user", "content": text_content}
        ]
    )
    return response.choices[0].message.content