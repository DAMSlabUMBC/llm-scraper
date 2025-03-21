import re
import ollama
import torch

def generate(entities):
    """
    generates triplets given a json of entities
    Input: entities ({"entities": [...]})
    Output: list of triplets ([...])
    """
    
    # initializes ollama client
    client = ollama.Client()
    
    # empties the cache
    torch.cuda.empty_cache()

    # prompts deepseek to make triplets given a json on entities
    response = client.chat(
        model='deepseek-r1:70b', 
        messages=[
            {
                'role': 'system',
                'content':
                """
                    You are a data engineer specialized in constructing knowledge graphs. Given a set of extracted entities, generate triplets in the format:

                ```
                [(('type1', 'entity1'), 'relationship', ('type2', 'entity2')), ...]
                ```

                ### **Strict Rules:**
                - **Output only the list of triplets.**  
                - **No explanations, bullet points, summaries, or additional text.**  
                - **Do not introduce or describe the output.**  
                - **If no valid triplets exist, return `[]` exactly.**

                ### **Entity Types:**
                - device, manufacturer, application, process, sensor, observation, inference, research, privacyPolicy, regulation  

                ### **Relationships:**
                - developedBy, manufacturedBy, compatibleWith, hasSensor, accessSensor, requiresSensor, performs, hasPolicy, statesInPolicy, captures, canInfer, showsInference, hasTopic, follows  

                ### **Triplet Schema:**
                ```
                application -> developedBy -> manufacturer
                device -> manufacturedBy -> manufacturer
                sensor -> manufacturedBy -> manufacturer
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
                inference -> showsInference -> research
                research -> references -> research
                research -> hasTopic -> process
                research -> hasTopic -> application
                research -> hasTopic -> observation
                research -> hasTopic -> sensor
                research -> hasTopic -> device
                privacyPolicy -> follows -> regulation
                ```

                ### **Example Input:**
                ```
                {"entities": ["Govee", "Govee Smart Light Bulbs", "Alexa", "WiFi", "Google Privacy Policy", "General Data Protection Regulation (GDPR)"]}
                ```

                ### **Expected Output:**
                ```
                [
                (('device', 'Govee Smart Light Bulbs'), 'manufacturedBy', ('manufacturer', 'Govee')),
                (('device', 'Govee Smart Light Bulbs'), 'compatibleWith', ('application', 'Alexa')),
                (('device', 'Govee Smart Light Bulbs'), 'hasSensor', ('sensor', 'WiFi')),
                (('application', 'Alexa'), 'hasPolicy', ('privacyPolicy', 'Google Privacy Policy')),
                (('privacyPolicy', 'Google Privacy Policy'), 'follows', ('regulation', 'General Data Protection Regulation (GDPR)'))
                ]
                ```

                **Output must strictly follow this format with no additional text.** If no valid triplets exist, return:  
                ```
                []
                ```

                """,
            },
            {
                'role': 'user',
                'content': entities,
            },
        ],
        stream=False
    )

    print(f"BEFORE PARSING <THINK> {response.message.content}")
    
    # removes think, json, and python tags
    removed_think_tags = remove_think_tags(response.message.content)
    return extract_python(extract_json(removed_think_tags))

def parse_string_to_list(input_string):
    """
    ensures triplets are in a list
    Input: input_string (text supposably as a list)
    Output: list of triplets or None if not in list format
    """
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
    #return cleaned_text.strip()

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
    # Use regex to remove ```json and ``` markers
    return re.sub(r'^```python\n?|```$', '', text, flags=re.MULTILINE).strip()