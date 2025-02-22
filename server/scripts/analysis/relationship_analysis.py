from setup import client
import re

def generate(entities):

    response = client.chat(
        model='deepseek-r1', 
        messages=[
            {
                'role': 'system',
                'content':
                """
                    You are a data engineer specialized in constructing knowledge graphs. You will recieve entities extracted from text, images, video, and code content.
                    You are tasked with generating a set of triplets strictly in the format ((type1, entity1), relationship, (type2, entity2)) by following these steps:

                    1. Determine the type of each entity. Entities are limited to the following: device, manufacturer, application, process, sensor, 
                    observation, inference, research, privacyPolicy, regulation. DO NOT PRINT A RESPONSE FOR THIS STEP

                    2. determine the types of relationships occuring between each entity. Relationships are limited to the following: developedBy, 
                    manufacturedBy, compatibleWith, hasSensor, accessSensor, requiresSensor, performs, hasPolicy, statesInPolicy, captures, canInfer, 
                    showsInference, hasTopic, follows. DO NOT PRINT A RESPONSE FOR THIS STEP

                    3. Form a set of triplets in the format (('type1', 'entity1'), 'relationship', ('type2', 'entity2')) by following the entity-relationship-entity
                    schema:
                    application -> developedBy -> manufacturer
                    device -> manufacturedBy -> manufacturer
                    sensor -> manufacturedBy -> manufactuerer
                    device -> compatibleWith -> application
                    device -> compatibleWith -> device
                    device -> hasSensor -> sensor
                    application -> accessSensor -> sensor
                    process -> requiresSensor -> sensor
                    device -> performs -> process
                    application -> performs -> process
                    device -> hasPolicy -> privacyPolicy
                    application -> hasPolicy -> privacyPolicy
                    manufacturer -> hasPolicy -> privacyPolicy
                    process -> statesInPolicy -> privacyPolicy
                    sensor -> statesInPolicy -> privacyPolicy
                    observation -> statesInPolicy -> privacyPolicy
                    sensor -> captures -> observation
                    observation -> canInfer -> inference
                    inference -> canInfer -> inference
                    inference -> showsReference -> research
                    research -> references -> research
                    research -> hasTopic -> process
                    research -> hasTopic -> application
                    research -> hasTopic -> observation
                    research -> hasTopic -> sensor
                    research -> hasTopic -> device
                    privacyPolicy -> follows -> regulation

                    Output: a set of triplets (('type1', 'name1'), relationship, ('type2', 'name2')) in a list or an empty list.
                    If no triplets are found, return an empty list ([]).
                    
                    Example 1:
                    Input:'
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
                    Output:'
                    [
                        (('device', 'Govee Smart Light Bulbs'), 'manufacturedBy', ('manufacturer', 'Govee')),
                        (('device', 'Light Bulb'), 'manufacturedBy', ('manufacturer', 'Govee')),
                        (('device', 'LED Light Bulbs'), 'manufacturedBy', ('manufacturer', 'Govee')),
                        (('device', 'A19'), 'manufacturedBy', ('manufacturer', 'Govee')),
                        (('device', 'Govee Smart Light Bulbs'), 'compatibleWith', ('application', 'Alexa')),
                        (('device', 'Govee Smart Light Bulbs'), 'compatibleWith', ('application', 'Google Assistant')),
                        (('device', 'Govee Smart Light Bulbs'), 'hasSensor', ('sensor', 'WiFi')),
                        (('device', 'Govee Smart Light Bulbs'), 'hasSensor', ('sensor', 'Bluetooth')),
                        (('application', 'Alexa'), 'accessSensor', ('sensor', 'Bluetooth')),
                        (('application', 'Google Assistant'), 'accessSensor', ('sensor', 'WiFi')),
                        (('device', 'Govee Smart Light Bulbs'), 'performs', ('process', 'activity tracking')),
                        (('device', 'Govee Smart Light Bulbs'), 'performs', ('process', 'location tracking')),
                        (('application', 'Google Assistant'), 'performs', ('process', 'activity tracking')),
                        (('device', 'Govee Smart Light Bulbs'), 'hasPolicy', ('privacyPolicy', 'Alexa Privacy Policy')),
                        (('device', 'Govee Smart Light Bulbs'), 'hasPolicy', ('privacyPolicy', 'Google Privacy Policy')),
                        (('application', 'Alexa'), 'hasPolicy', ('privacyPolicy', 'Alexa Privacy Policy')),
                        (('application', 'Google Assistant'), 'hasPolicy', ('privacyPolicy', 'Google Privacy Policy')),
                        (('manufacturer', 'Govee'), 'hasPolicy', ('privacyPolicy', 'Alexa Privacy Policy')),
                        (('manufacturer', 'Govee'), 'hasPolicy', ('privacyPolicy', 'Google Privacy Policy')),
                        (('process', 'activity tracking'), 'statesInPolicy', ('privacyPolicy', 'Google Privacy Policy')),
                        (('process', 'location tracking'), 'statesInPolicy', ('privacyPolicy', 'Alexa Privacy Policy')),
                        (('sensor', 'WiFi'), 'captures', ('observation', 'lighting preferences')),
                        (('sensor', 'Bluetooth'), 'captures', ('observation', 'sleep patterns')),
                        (('sensor', 'Bluetooth'), 'captures', ('observation', 'potential health concerns')),
                        (('observation', 'voice recordings are collected and stored'), 'statesInPolicy', ('privacyPolicy', 'Google Privacy Policy')),
                        (('observation', 'voice recordings are collected and stored'), 'statesInPolicy', ('privacyPolicy', 'Alexa Privacy Policy')),
                        (('device', 'Govee Smart Light Bulbs'), 'hasPolicy', ('privacyPolicy', 'Alexa Privacy Policy')),
                        (('privacyPolicy', 'Alexa Privacy Policy'), 'follows', ('regulation', 'California Consumer Privacy Act (CCPA)')),
                        (('device', 'Govee Smart Light Bulbs'), 'hasPolicy', ('privacyPolicy', 'Google Privacy Policy')),
                        (('privacyPolicy', 'Google Privacy Policy'), 'follows', ('regulation', 'General Data Protection Regulation (GDPR)')),
                        (('privacyPolicy', 'Google Privacy Policy'), 'follows', ('regulation', 'Personal Information Protection and Electronic Documents Act (PIPEDA)'))
                    ]'

                    
                    DO NOT RETURN THE WORD 'JSON' or any other word in the beginning of your response, stricly output the relationships you've created similar to the example output.
                """,
            },
            {
                'role': 'user',
                'content': entities,
            },
        ],
        stream=False
    )
    return response.message.content

def parse_string_to_list(input_string):
    # Step 1: Remove unnecessary whitespace and normalize the input string
    input_string = input_string.strip()
    
    # Step 2: Replace spaces in multi-word entities with camel-case format
    # Example: 'Govee Smart Light Bulbs' -> 'GoveeSmartLightBulbs'
    input_string = re.sub(r"'([a-zA-Z]+(?:\s+[a-zA-Z]+)+)'", 
                          lambda m: f"'{''.join(word.capitalize() for word in m.group(1).split())}'", 
                          input_string)
    
    # Step 3: Evaluate the string to transform it into a Python object (list of tuples)
    try:
        parsed_list = eval(input_string)
    except SyntaxError as e:
        print("Error parsing string:", e)
        return None
    
    # Step 4: Convert each tuple into the expected string format
    result = [
        str(item).replace(" ", "")  # Remove extra spaces for compact formatting
        for item in parsed_list
    ]
    
    return result