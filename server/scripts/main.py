import sys
sys.dont_write_bytecode = True
from scraping import scrape_website
from analysis.image_analysis import analyze_image_elements
from analysis.entity_analysis import analyze_text_elements
from analysis.relationship_analysis import generate
from util.llm_utils.response_cleaner import parse_string_to_list
from KG import createKG
from util.scraper.scrapping_manager import ScrappingManager
import time
import os
import logging
import argparse
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    filename='amazon_scraper.log',  # Log file name
    filemode = "a",
    level=logging.INFO,  # Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
)


# all defined modules
AmazonModule = "Amazon"

RETRIES = 3

def main():

    
    html = ""
    text_result = {"entities": []}
    image_result = {"entities": []}
    video_result = {"entities": []}
    code_result = {"entities": []}

    # initializes argument parser
    parser = argparse.ArgumentParser(description="Process an input file and save output.")
    
    # Adding input and output arguments
    parser.add_argument("--input_folder", required=True, help="Path to the input file")
    parser.add_argument("--output_file", required=True, help="Path to save the output file")
    parser.add_argument("--ollama_port", type=int, help="Port number for Ollama")


    # parses the arguments
    args = parser.parse_args()

    # sets the input and output files
    batch_folder = args.input_folder
    output = args.output_file

    # scraping urls and htmls should be done locally before doing all llm extraction stuff in ADA
    """# makes a new url extractor
    url_extractor = ScrappingManager()

    # initializes the modules the user wants to add to the url extractor
    url_extractor.initializeModule(AmazonModule)

    # fetches the urls of a module
    URL_set = url_extractor.getProductURLs(AmazonModule, "search_queries.txt")

    print(URL_set)

    URL_list = list(URL_set)[:5]"""
    
    with open(output, "w") as file:
        print("EMPTYING TRIPLETS FILE")
    
    start_time = time.time()
    
    # gets all the html code in a specific batch
    entries = list(os.scandir(batch_folder))
    
    # iterates through each html file
    for i in tqdm(range(len(entries))):
        print(f"HTML {entries[i]}")
        with open(entries[i], "r") as f:
            html = f.read()
            
        # scrapes the text, images, code, and video contents
        text_content, image_content, code_content, video_content = scrape_website(html, AmazonModule)

        if text_content == "" and image_content == "" and code_content == "" and video_content == "":
            exit()

        if text_content == "{'name': None, 'manufacturer': None, 'details': ''}":
            logging.error(f"Error extracting contents from {entries[i]}")
            continue

        # extracts text entities if there's text content
        if text_content != "{'name': None, 'manufacturer': None, 'details': ''}":
            text_result = analyze_text_elements(text_content)
            print("finished text")
        
        # extracts video entities if there's video content
        if video_content != "":
            video_result = analyze_text_elements(video_content)
            print("finished video")

        # extracts code entities if there's code content
        if code_content != "[]":
            code_result = analyze_text_elements(code_content)
            print("finished code")

        # extracts image entities if there's image content
        if image_content != []:
            image_result = analyze_image_elements(image_content)
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
            generate_result = generate(str(entities))

            result_list = parse_string_to_list(generate_result)
            if isinstance(result_list, list):
                break
        
        # returns empty list of triplets if fails to generate entities for number of retries
        if not isinstance(result_list, list):
            result_list = []

        print('[😻] Final Response: ', result_list)

        triplets_list = []

        for triplet in result_list:
            default_weight = 0.5
            triplets_list.append(str(triplet + (default_weight,)))
        
        # appends the triplets into designated triplet file
        with open(output, "a") as file:
            for triplet in triplets_list:
                file.writelines(str(triplet))
                file.write("\n")
                
    end_time = time.time()
    
    print("elapsed time:", end_time - start_time)
            
if __name__ == "__main__":
    main()