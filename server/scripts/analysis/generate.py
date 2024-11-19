from setup import client
import re

def generate(text_result, video_result, image_result, code_result):

    content = f"""
    Text: {text_result}
    Video: {video_result}
    Image: {image_result}
    Code: {code_result}
    """

    #print("content")
    #print(content)

    # original prompt: Create a knowledge graph from all of the provided entities.
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """
You are a data engineer specialized in constructing knowledge graphs. You are given a content from text, images, video, and code. Generate a set of triplets in the format ((type1, entity1), relationship, (type2, entity2)) by following these steps:
1. determine the type of each entity. Entities are limited to the following: device, manufacturer, application, process, sensor, observation, inference, research, privacyPolicy, regulation. DO NOT PRINT A RESPONSE FOR THIS STEP
2. determine the types of relationships occuring between each entity. Relationships are limited to the following: developedBy, manufacturedBy, compatibleWith, hasSensor, accessSensor, requiresSensor, performs, hasPolicy, statesInPolicy, captures, canInfer, showsInference, hasTopic, follows. DO NOT PRINT A RESPONSE FOR THIS STEP
3. Form a set of triplets in the format ((type1, entity1), relationship, (type2, entity2)) by following the entity-relationship-entity schema:
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

If no triplets are found, return an empty list ([]).

Output: a set of triplets ((type1, name1), relationship, (type2, name2)) or an empty list.
                                        """
            },
            {"role": "user", "content": content}
        ]
    )
    return response.choices[0].message.content

def parse_string_to_list(input_string):
    # Step 1: Add quotes around unquoted words using regex
    # Matches any alphanumeric word or slash-separated words not already quoted
    formatted_string = re.sub(r'(?<!")\b[a-zA-Z0-9_/]+\b(?!")', r'"\g<0>"', input_string)

    # Step 2: Replace square brackets for the list and clean up the parentheses
    formatted_string = formatted_string.replace("[", "[").replace("]", "]")

    # Step 3: Safely evaluate the formatted string into a Python object
    try:
        parsed_list = eval(formatted_string)
    except SyntaxError as e:
        print("Error parsing string:", e)
        return None

    return parsed_list