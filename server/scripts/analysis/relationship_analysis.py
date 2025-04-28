import re
import ollama
import torch
from util.llm_utils.response_cleaner import extract_json, extract_python, remove_think_tags

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
                device -> isCategory -> category
                ```
                Note: This is a non-exhaustive list of the schema. Feel free to add more beyond the static schema as long as you follow the triplet format.

                ### **Example Input:**
                ```
                {"entities": ["Govee", "Govee Smart Light Bulbs", "Alexa", "WiFi", "Google Privacy Policy", "General Data Protection Regulation (GDPR)"]}
                ```

                ### **Expected Output:**
                ```
                [
                (('device', 'Govee Smart Light Bulbs'), 'manufacturedBy', ('manufacturer', 'Govee')),
                (('device', 'Govee Smart Light Bulbs'), 'compatibleWith', ('application', 'Alexa')),
                (('device', 'Govee Smart Light Bulbs'), 'isCategory', ('category', 'Smart Lighting')),
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
