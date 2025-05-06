import re
import ollama
import torch
from util.llm_utils.response_cleaner import extract_json, extract_python, remove_think_tags
import ast
import random
import os
import argparse
from tqdm import tqdm

FOLDER = "analysis_output"
RETRIES = 3

def product_classify(text_content):
    """
    generates triplets given a json of entities
    Input: entities ({"entities": [...]})
    Output: list of triplets ([...])
    """

    #text_dict = ast.literal_eval(text_content)

    product_name = text_content.get("product_name")

    if not product_name:
        return False
    
    # initializes ollama client
    client = ollama.Client()

    for i in range(RETRIES):
    
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
                    Product Classification Task  
Return only IOT or NOT-IOT. No explanation. No extra words. No punctuation.

Examples:
Amazon Echo Dot -> IOT  
Apple Watch Strap -> NOT-IOT  
Google Nest Thermostat -> IOT  
Canon EOS Rebel Camera -> NOT-IOT  
August Smart Lock Pro -> IOT  

Now classify:
{product_name} ->
                    """,
                },
                {
                    'role': 'user',
                    'content': product_name,
                },
            ],
            stream=False
        )
    
        #print(f"BEFORE PARSING <THINK> {response.message.content}")
        
        # removes think, json, and python tags
        removed_think_tags = remove_think_tags(response.message.content)
    
    
        answer = removed_think_tags.upper()
    
        print(f"text_content {product_name}")
        print(f"output {answer}")

        if answer.strip()[-7:] == "NOT-IOT":
            return False
        elif answer.strip()[-3:] == "IOT":
            return True
    return False

if __name__ == "__main__":

    # initializes the parser
    parser = argparse.ArgumentParser(description="Process an input file and save output.")
    parser.add_argument("--input_file", required=True, help="json with configurations to a specific site")
    parser.add_argument("--output_file", required=True, help="path to obtain the batch urls")

    args = parser.parse_args()

    input_file = args.input_file
    output_file = args.output_file

    # opens the test file
    with open(input_file, "r", encoding="utf-8", errors="replace") as f:
        text_contents = f.readlines()

    random.shuffle(text_contents)
    text_contents = text_contents[:50]
    with open(os.path.join(FOLDER, output_file), "w", encoding="utf-8") as f:
        for content in tqdm(text_contents):

            try:
                # Step 1: Quote the URL if needed
                content_fixed = re.sub(r'(https?://[^\s)]+)', r"'\1'", content.strip())
    
                # Step 2: Split into dict string and URL string
                dict_str, url = content_fixed.rsplit(" ", 1)
    
                # Step 3: Safely evaluate the dictionary string
                text_content = ast.literal_eval(dict_str)
    
                # Step 4: Classify product
                result = product_classify(text_content)
    
                # Step 5: Write output
                f.write(f"{text_content} | {url} | {result}\n")
    
            except Exception as e:
                print(f"❌ Failed to parse line:\n{content}\nError: {e}\n")
                continue
            