#from validation.search_validation import search_validation_method
from search_validation_playwright import search_validation_method
#from validation.llm_validation import llm_validation_method
from llm_validation_playwright import llm_validation_method
from datetime import datetime

import argparse
import os
import ast
import torch

if __name__ == "__main__":

    # initializes the parser
    parser = argparse.ArgumentParser(description="Process an input file and save output.")

    # Adding input and output arguments
    parser.add_argument("--input_file", required=True, help="file that has all the triples")
    parser.add_argument("--output_file", required=True, help="file that will output the triples and their corresponding weights")

    # parses the arguments
    args = parser.parse_args()

    # sets the input and output files
    input_file = args.input_file
    output_file = args.output_file

    # reads the triples from the input file
    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    result_list = []
    # parses out the triples from lines
    for line in lines:
        triple = line.split()[0]
        result_list.append(triple)

    triplets_list = []


    for triplet_str in result_list:

        triplet = ast.literal_eval(triplet_str)
        #triplet = (('device', 'Govee Smart Light Bulbs'), 'manufacturedBy', ('manufacturer', 'Govee'))

        print("Getting weight")
        weight = 0


        # TODO: These validation methods use google, resulting in capcha

        # Validate with wikidata, does not exist? Use our other validation methods 
        if weight < 50:
            try:
                weight = search_validation_method(triplet) or 0
            except Exception as e:
                print(f"ERROR IN SEARCH VALIDATION {e}")
                weight = 0
        
        if weight < 50:
            try:
                weight = llm_validation_method(triplet) or 0
            except Exception as e:
                print(f"ERROR IN LLM VALIDATION {e}")
                weight = 0
        exit()


        default_weight = weight
        print("Triple Weight: ", weight)
        triplets_list.append(f"{triplet} {default_weight}")
            
    # appends the triplets into designated triplet file
    with open(output_file, "a") as file:
        for triplet in triplets_list:
            file.writelines(str(triplet))
            file.write("\n")