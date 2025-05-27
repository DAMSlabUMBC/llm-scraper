import ollama
import torch
import json
from util.llm_utils.response_cleaner import extract_json, extract_python, remove_think_tags
import re
import ast
import random
import os
import argparse
from tqdm import tqdm


RETRIES = 3

PROMPTS_FOLDER = "prompts"
OUTPUT_FOLDER = "analysis_output"

#ENTITIES_PATTERN = r"^\{'entities': \[(?:'(?:[^']*)'(?:, )?)*\]\}$"
ENTITIES_PATTERN = r"\[.*?\]"

def analyze_text_elements(text_content, prompt):

    print(f"TEXT CONTENT {text_content}")
    
    entities_json = {"entities": []}

    # initializes ollama client
    client = ollama.Client()

    # generates entities for number of retries
    for i in range(RETRIES):
    
        # empties the cache
        torch.cuda.empty_cache()

        # generates entities given some text_content
        response = client.chat(
            model='mistral:7b-instruct', 
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

        # Clean and extract the message
        raw_response = response["message"]["content"]
        removed_think_tags = remove_think_tags(raw_response)
        removed_json_tags = extract_json(extract_python(removed_think_tags))

        print(f"OUTPUT: {removed_json_tags}")

        # First try: strict JSON parsing
        try:
            parsed = json.loads(removed_json_tags.strip())
            if isinstance(parsed, dict) and "entities" in parsed and isinstance(parsed["entities"], list):
                if all(isinstance(e, str) for e in parsed["entities"]):
                    entities_json = parsed
                    break  # Valid structured response found
        except json.JSONDecodeError as e:
            print(f"❌ JSON decoding failed: {e}")

            # Fallback: use regex to extract list directly
            list_match = re.search(ENTITIES_PATTERN, removed_json_tags)
            if list_match:
                try:
                    list_str = list_match.group()
                    entity_list = json.loads(list_str.replace("'", '"'))  # convert to valid JSON list if needed
                    if isinstance(entity_list, list) and all(isinstance(e, str) for e in entity_list):
                        entities_json["entities"] = entity_list
                        break
                except Exception as fallback_err:
                    print(f"⚠️ Regex-based fallback failed: {fallback_err}")

    if entities_json == {"entities": []}:
        print("⚠️ No valid entities extracted after retries.")

    print(f"ENTITIES: {entities_json}")
    return entities_json

def parse_content_line(line):
    """
    Parses a line formatted as: {dict} <space> URL
    Safely extracts and evaluates the dictionary portion and URL string.
    """
    try:
        # Match the URL (requires at least one http/https link at the end)
        match = re.search(r"(https?://[^\s]+)$", line.strip())
        if not match:
            raise ValueError("No URL found.")

        url = match.group(1)

        # Get everything before the URL
        dict_str = line[:match.start()].strip()

        # Fix trailing commas if present
        if dict_str.endswith(","):
            dict_str = dict_str[:-1]

        # Evaluate just the dictionary portion
        text_dict = ast.literal_eval(dict_str)

        return text_dict, url

    except Exception as e:
        print(f"❌ Failed to parse line: {e}")
        return None, None

if __name__ == "__main__":
    # initializes the parser
    parser = argparse.ArgumentParser(description="testing the effectiveness of the prompt")
    parser.add_argument("--input_file", required=True, help="file with sample text content to test")
    parser.add_argument("--output_file", required=True, help="file to output results")
    parser.add_argument("--prompt_folder", required=True, help="filw which holds the prompt to test")

    args = parser.parse_args()

    input_file = args.input_file
    output_file = args.output_file
    prompt_folder = args.prompt_folder

    # opens the test file
    with open(input_file, "r", encoding="utf-8", errors="replace") as f:
        text_contents = f.readlines()

    # extracts the prompt
    with open(os.path.join(PROMPTS_FOLDER, prompt_folder, "entity_analysis.txt"), "r", encoding="utf-8") as f:
        prompt = f.read()

    random.shuffle(text_contents)
    text_contents = text_contents[:50]
    with open(os.path.join(OUTPUT_FOLDER, output_file), "a", encoding="utf-8") as f:
        for content in tqdm(text_contents):

            text_dict, url = parse_content_line(content)
            if not text_dict:
                continue
            result = analyze_text_elements(text_dict, prompt)
            f.write(f"{text_dict} | {url} | {result}\n")

            # Use regex to surround the URL with quotes
            # content_fixed = re.sub(r'(https?://[^\s)]+)', r"'\1'", content)
            # content_tuple = ast.literal_eval(content_fixed.strip())
            # text_content, url = content_tuple
            
            # result = analyze_text_elements(text_content, prompt)
            # f.write(f"{text_content} {url} {result}\n")
