import sys
sys.dont_write_bytecode = True
from analysis.image_analysis import analyze_image_elements
from analysis.entity_analysis import analyze_text_elements
from analysis.relationship_analysis import generate
from analysis.iot_classification import product_classify
from util.llm_utils.response_cleaner import parse_string_to_list
from KG import createKG
from datetime import datetime

#from util.scraper.scrapping_manager import ScrappingManager
#from util.scraper.content_scraper import scrape_website
from scrape_with_config import scrape_website
from validation.search_validation import search_validation_method
from validation.llm_validation import llm_validation_method

import time
import requests
import os
import logging
import argparse
import ast
from tqdm import tqdm
import json
from arango.exceptions import AQLQueryExecuteError
import ast

# Configure logging
logging.basicConfig(
    filename='amazon_scraper.log',  # Log file name
    filemode = "a",
    level=logging.INFO,  # Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
)

# all defined modules
AmazonModule = "Amazon"
CONFIGS_FOLDER = "config_files"
PROMPTS_FOLDER = "prompts"

RETRIES = 3

def main():
    video_content = ""
    code_content = "[]"
    image_content = []
    text_content = "{}"

    text_result = {"entities": []}
    image_result = {"entities": []}
    video_result = {"entities": []}
    code_result = {"entities": []}

    # initializes argument parser
    parser = argparse.ArgumentParser(description="Process an input file and save output.")
    
    # Adding input and output arguments
    parser.add_argument("--config_file", required=True, help="json with configurations to a specific site")
    parser.add_argument("--batch_file", required=True, help="path to obtain the batch urls")
    parser.add_argument("--output_file", required=True, help="Path to save the output file")
    parser.add_argument("--ollama_port", type=int, help="Port number for Ollama")

    # parses the arguments
    args = parser.parse_args()

    # sets the input and output files
    config_file = args.config_file
    batch_file = args.batch_file
    output_file = args.output_file
    #extracted_file = args.extracted_file

    # extracts the contents of the configs file
    with open(os.path.join(CONFIGS_FOLDER, config_file), 'r') as f:
        configs = json.load(f)


    # gets the appropriate prompts for the specific website
    with open(os.path.join(PROMPTS_FOLDER, configs["type"], "entity_analysis.txt"), "r", encoding="utf-8") as f:
        entity_prompt = f.read()

    with open(os.path.join(PROMPTS_FOLDER, configs["type"], "relationship_analysis.txt"), "r", encoding="utf-8") as f:
        relationship_prompt = f.read()

    # gets the product_urls from the batch
    # with open(extracted_file, "r") as f:
    #     #product_urls = f.readlines()
    #     text_contents = f.readlines()

    # gets the product_urls from the batch
    with open(batch_file, "r") as f:
        #product_urls = f.readlines()
        extracted_content = f.readlines()

    start_time = time.time()
    
    # iterates through each url
    for content in tqdm(extracted_content):

        content = content.strip()
        #url = url.strip()
        # text_content = text_contents[i].strip()
        # url = product_urls[i].strip()

        text_content, url = content.rsplit(" ", 1)
            
        # scrapes the text, images, code, and video contents
        #text_content, image_content, code_content, video_content = scrape_website(url, AmazonModule)
        #text_content = scrape_website(url, configs)

        # if text_content == "{}":
        #     logging.error(f"Error extracting contents from {url}")
        #     continue

        print(text_content)

        # with open(output_file, "a") as file:
        #     file.writelines(str(text_content))
        #     file.write("\n")
        # continue

        # checks if the device is IoT (eccomerce)
        if configs["type"] =="ecommerce":
            data = ast.literal_eval(text_content)
            iot = product_classify(data)
            if not iot:
                print("product is not an IoT device")
                continue
        
        # extracts text entities if there's text content
        if text_content != "{}":
            text_result = analyze_text_elements(text_content, entity_prompt)
            print("finished text")
        
        # extracts video entities if there's video content
        if video_content != "":
            video_result = analyze_text_elements(video_content, entity_prompt)
            print("finished video")

        # extracts code entities if there's code content
        if code_content != "[]":
            code_result = analyze_text_elements(code_content, entity_prompt)
            print("finished code")

        # extracts image entities if there's image content
        if image_content != []:
            image_result = analyze_image_elements(image_content, entity_prompt)
            print("finished images")
        
        print("\n=== Analysis Results ===")
        print("Text Analysis:", text_result)
        print("Code Analysis:", code_result)
        print("Video Analysis:", video_result)
        print("Image Analysis:", image_result)
        print("=====================\n")
        

        print('\n\n\n\n\n\n')

        entities = {"entities": set()}

        # adds all text, image, video, and code entities in a single set of entities
        entities["entities"].update(text_result["entities"])
        entities["entities"].update(video_result["entities"])
        entities["entities"].update(image_result["entities"])
        entities["entities"].update(code_result["entities"])
        
        print("Entities:",entities)

        result_list = None

        # generates triplets for number of retries
        for i in range(RETRIES):

            # generates triplets
            generate_result = generate(str(entities), relationship_prompt)

            result_list = parse_string_to_list(generate_result)
            if isinstance(result_list, list):
                break
        
        # returns empty list of triplets if fails to generate entities for number of retries
        if not isinstance(result_list, list):
            result_list = []

        print('[😻] Final Response: ', result_list)

        triplets_list = []

        # TODO: This should be made into a function either here or in the validation methods
        for triplet_str in result_list:

            # triplet = ast.literal_eval(triplet_str)
            triplet = (('device', 'Govee Smart Light Bulbs'), 'manufacturedBy', ('manufacturer', 'Govee'))

            print("Getting weight")
            weight = 0


            # TODO: These validation methods use google, resulting in capcha

            # Validate with wikidata, does not exist? Use our other validation methods 
            if weight < 50:
                try:
                    weight = search_validation_method(triplet) or 0
                except Exception:
                    weight = 0
            
            if weight < 50:
                try:
                    weight = llm_validation_method(triplet) or 0
                except Exception:
                    weight = 0


            default_weight = weight
            print("Triple Weight: ", weight)
            triplets_list.append(f"{triplet} {default_weight} {url} {datetime.now()}")
        
        print(triplets_list)
        # appends the triplets into designated triplet file
        with open(output_file, "a") as file:
            for triplet in triplets_list:
                file.writelines(str(triplet))
                file.write("\n")
                
    end_time = time.time()
    
    print("elapsed time:", end_time - start_time)
            
if __name__ == "__main__":
    main()