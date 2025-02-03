from setup import client
import re

def generate(entities):

    # original prompt: Create a knowledge graph from all of the provided entities.
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": """
    You are a data engineer specialized in constructing knowledge graphs. You are given a content from text, images, video, and code. Generate a set of triplets in the format ((type1, entity1), relationship, (type2, entity2)) by following these steps:
    1. determine the type of each entity. Entities are limited to the following: device, manufacturer, application, process, sensor, 
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

    Do not include the word json in front of your result.
    If no triplets are found, return an empty list ([]).

    Output: a set of triplets (('type1', 'name1'), relationship, ('type2', 'name2')) in a list or an empty list.
    
    DO NOT RETURN THE WORD 'JSON' in the beginning of your response.
                                        """
            },
            {"role": "user", "content": entities}
        ]
    )
    return response.choices[0].message.content

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