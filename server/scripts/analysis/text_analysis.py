from setup import client
import spacy

def analyze_text_elements(text_content):

    # Load English tokenizer, tagger, parser and NER
    nlp = spacy.load("en_core_web_lg")
    
    doc = nlp(text_content)

    spaCy_content = ""

    # Find named entities, phrases and concepts
    for entity in doc.ents:
        # print(entity.text, entity.label_)
        spaCy_content+= entity.text + " "

    combined_content = f"""
        Text: {text_content}
        spaCy: {spaCy_content}
    """

    print("Combined Content:", combined_content)



    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """
                                            You will receive an input of text and a list of entities created by spaCy (for example, named entities like organizations, people, products, locations, or any other spaCy-detected items).

Your job is to:
1. Identify and extract all entities related to IoT within the input text—especially devices (e.g. cameras, smart speakers, phones), manufacturers (e.g. Apple, Google, Amazon), sensors, applications, etc.—**as well as** any other entities that spaCy already recognized in the input.
2. Return them in JSON format, specifically: `{ "entities": [list of entities] }`.
3. If no entities are found, return `{ "entities": [] }`.

**Important requirements**:
- **Do not change, add, or modify any part of the input text**. Only extract entities that appear in the text or are identified by spaCy.
- **Do not output additional explanations or examples** beyond the JSON result. End your answer immediately after producing the JSON.
- Here is the expected style:

Example 1:
Input: `Earth is the third biggest planet in our solar system.`
Output: `{ "entities": ["Earth", "solar system"] }`

Example 2:
Input: `There are no entities here.`
Output: `{ "entities": [] }`

Always follow this response format, but with a special focus on capturing IoT-related references (devices, manufacturers, sensors, applications, processes) if they appear.


                            """
            },
            {"role": "user", "content": combined_content}
        ]
    )
    return response.choices[0].message.content