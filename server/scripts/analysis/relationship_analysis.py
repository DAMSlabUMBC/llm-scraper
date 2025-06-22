import re
import ollama
import torch
from util.llm_utils.response_cleaner import extract_json, extract_python, remove_think_tags, parse_string_to_list
import re
import ast
import random
import os
import argparse
from tqdm import tqdm


RETRIES = 3

PROMPTS_FOLDER = "prompts"
OUTPUT_FOLDER = "analysis_output"

TRIPLET_PATTERN = r"""
\(\(\s*['"`]([^'"`]+)['"`]\s*,\s*['"`]([^'"`]+)['"`]\s*\)\s*,      # Subject
\s*['"`]([^'"`]+)['"`]\s*,                                      # Predicate
\s*\(\s*['"`]([^'"`]+)['"`]\s*,\s*['"`]([^'"`]+)['"`]\s*\)\)       # Object
"""

def generate(entities, prompt, text=""):
    """
    generates triplets given a json of entities
    Input: entities ({"entities": [...]})
    Output: list of triplets ([...])
    """
    #print(f"ENTITIES: {entities}")
    if text != "":
        text_content = f"{text} entities: {entities}"
    else:
        text_content = str(entities)
    
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
                'content': f"{prompt}",
            },
            {
                'role': 'user',
                'content': str(text_content),
            },
        ],
        stream=False
    )

    #print(f"BEFORE PARSING <THINK> {response.message.content}")
    
    # removes think, json, and python tags
    removed_think_tags = remove_think_tags(response.message.content)
    remove_python_tags = extract_python(extract_json(removed_think_tags))

    print(f"EXTRACTED TRIPLETS: {remove_python_tags}")

    matches = re.findall(TRIPLET_PATTERN, remove_python_tags, flags=re.VERBOSE)

    triplets = [
        ((subj_type, subj_ent), pred, (obj_type, obj_ent))
        for subj_type, subj_ent, pred, obj_type, obj_ent in matches
    ]

    # fallback: converts the string to a python list
    if triplets == []:
        print("attempting fallback: convert to python list")

        # converts the generated triplets into a python list
        try:
            triplets = ast.literal_eval(remove_python_tags)
            print("Extracted triplets successfully:")
        except Exception as e:
            print("Failed to parse triplets:", e)

    print(f"TRIPLETS {triplets}")

    return str(triplets)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="testing the effectiveness of the prompt")
    parser.add_argument("--input_file", required=True, help="file with sample text content to test")
    parser.add_argument("--output_file", required=True, help="file to output results")
    parser.add_argument("--prompt_folder", required=True, help="filw which holds the prompt to test")

    args = parser.parse_args()

    input_file = args.input_file
    output_file = args.output_file
    prompt_folder = args.prompt_folder

    # opens the test file
    with open(os.path.join("analysis_output", input_file), "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    # extracts the prompt
    with open(os.path.join(PROMPTS_FOLDER, prompt_folder, "relationship_analysis.txt"), "r", encoding="utf-8") as f:
        prompt = f.read()

    random.shuffle(lines)
    lines = lines[:50]
    with open(os.path.join(OUTPUT_FOLDER, output_file), "a", encoding="utf-8") as f:
        for line in tqdm(lines):

            url = line.split(" | ")[1].strip()
            entities = line.split(" | ")[2].strip()

            result_list = None

            for i in range(RETRIES):
        
                # generates triplets
                generate_result = generate(str(entities), prompt)
        
                result_list = parse_string_to_list(generate_result)
                if isinstance(result_list, list):
                    if result_list != []:
                        break
            
            # returns empty list of triplets if fails to generate entities for number of retries
            if not isinstance(result_list, list):
                result_list = []
        
            print('[😻] Final Response: ', result_list)
            f.write(f"{entities} | {url} | {result_list}\n")