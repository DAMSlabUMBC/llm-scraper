import os
import ollama
import torch
import re
import ast
from fuzzywuzzy import fuzz
from tqdm import tqdm
import argparse

RETRIES = 3

def map_content_with_triplets(extracted_lines, triplets_lines):
    data = {}

    # adds url and text content to data
    for line in extracted_lines:
        text_content, url = line.rsplit(" ", 1)
        if url not in data:
            data[url] = {"text_content": text_content, "triplets": []}

    for line in triplets_lines:
        triplet = line.split()[0]
        url = line.split()[2]
        if url in data:
            data[url]["triplets"].append(triplet)

    return data

def compute_precision(combined_input):

    # initializes ollama client
    client = ollama.Client()

    for i in range(RETRIES):
    
        # empties the cache
        torch.cuda.empty_cache()

        # generates entities given some text_content
        response = client.chat(
            model='mistral:7b-instruct', 
            messages=[
                {
                    'role': 'system',
                    'content': """
                    You will be given product information in a JSON-like dictionary and a list of triplets extracted from that product information.\n
                    Count how many triplets are correct according to the product information.
                    Only consider a triplet correct if all three components (subject, predicate, object) are clearly supported by the product text.\n
                    Return only the number of correct triplets as an integer.
                """,
                },

                {
                    'role': 'user',
                    'content': str(combined_input),
                },
            ],
            stream=False
        )
        
        precision = response["message"]["content"]

        if precision.isdigit():
            return int(precision)

    return None

def compute_recall(combined_input):

    # initializes ollama client
    client = ollama.Client()

    for i in range(RETRIES):
    
        # empties the cache
        torch.cuda.empty_cache()

        # generates entities given some text_content
        response = client.chat(
            model='mistral:7b-instruct', 
            messages=[
                {
                    'role': 'system',
                    'content': """
                    You will be given a product description as a dictionary and a list of extracted triplets.

                    Each triplet is formatted as: 
                    (('type1', 'entity1'), 'relationship', ('type2', 'entity2'))

                    Your task is to estimate how many additional valid triplets could have been extracted from the product description but were **not** included in the provided list.

                    - Do **not** explain your reasoning.
                    - Do **not** output anything except a single integer (e.g., `3`).
                    - Do **not** include units, words, or punctuation.

                    Return only an integer.

                    Example:
                    Input:
                    {
                        'text_content': {
                            'product_name': 'Amazon Echo Dot',
                            'features': 'Smart speaker with Alexa. Supports voice commands, Wi-Fi, and Bluetooth. Compatible with smart home devices.'
                        },
                        'triplets': [
                            (('device', 'Amazon Echo Dot'), 'compatibleWith', ('application', 'Alexa')),
                            (('device', 'Amazon Echo Dot'), 'hasFeature', ('feature', 'Voice Commands'))
                        ]
                    }
                    Output:
                    3
                """,
                },

                {
                    'role': 'user',
                    'content': str(combined_input),
                },
            ],
            stream=False
        )
        
        recall = response["message"]["content"]

        if recall.isdigit():
            return int(recall)
        
    return None

def extract_sentences_from_text_content(text_content_str):
    # Convert the string to a proper dictionary
    content_dict = ast.literal_eval(text_content_str)

    # Concatenate all values from the dictionary
    full_text = ""
    for val in content_dict.values():
        if isinstance(val, str):
            full_text += " " + val

    # Replace pipes and tabs with sentence separators
    cleaned_text = full_text.replace('|', '. ').replace('\\t', '. ').replace('\t', '. ')

    # Use regex to split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', cleaned_text.strip())

    # Optional: remove empty or overly short entries
    sentences = [s.strip() for s in sentences if len(s.strip()) > 5]

    return sentences

def compute_precision_fuzzy(sentences, str_triplets, threshold=70):

    correct_count = 0

    triplets = []
    for triplet in str_triplets:
        triplet = ast.literal_eval(triplet)
        triplets.append(triplet)


    correct_count = 0
    for subj, pred, obj in triplets:
        triplet_str = f"{subj[1]} {pred} {obj[1]}".lower()
        for sentence in sentences:
            similarity = fuzz.partial_ratio(triplet_str.lower(), sentence.lower())
            if similarity >= threshold:
                correct_count += 1
                break

    return correct_count
    

if __name__ == "__main__":

    total_precision_ai = 0
    total_precision_fuzzy = 0
    total_recall = 0
    total_f1_ai = 0
    total_f1_fuzzy = 0
    count = 0

    # intializes the parser
    parser = argparse.ArgumentParser(description="Process an input file and save output.")

    parser.add_argument("--extracted_file", required=True, help="file with extracted content")
    parser.add_argument("--triplets_file", required=True, help="file with extracted triplets")
    parser.add_argument("--preprocessed_file", required=True, help="file with mapped out text content and triplets")
    parser.add_argument("--output_file", required=True, help="output file of the results")

    args = parser.parse_args()

    extracted_file = args.extracted_file
    triplets_file = args.triplets_file
    preprocessed_file = args.preprocessed_file
    output_file = args.output_file

    # opens the file for extracted content
    with open(extracted_file, "r", encoding="utf-8") as f:
        extracted_lines = [line.strip() for line in f.readlines()]
    
    # opens the file for triplets
    with open(triplets_file, "r", encoding="utf-8") as f:
        triplets_lines = [line.strip() for line in f.readlines()]

    data = map_content_with_triplets(extracted_lines, triplets_lines)

    with open(preprocessed_file, "w", encoding="utf-8") as f:
        for url in data:
            f.write(f"{url} {str(data[url])}\n")

    # iterates through each product to calculate precision and recall
    with open(output_file, "w", encoding="utf-8") as f:
        for url in tqdm(data):
            text_content = data[url]["text_content"]
            triplets = data[url]["triplets"]

            # computes precision with AI
            precision_ai = compute_precision(data[url])
            if len(triplets) > 0 and precision_ai is not None:
                tp = precision_ai  # correct triplets
                fp = len(triplets) - tp
                precision_score_ai = tp / (tp + fp) if (tp + fp) else 0
            else:
                precision_score_ai = None
            f.write(f"URL: {url}\n")
            f.write(f"Precision with Mistral:7b-Instruct\n")
            f.write(f"Number of extracted triplets: {len(triplets)}\n")
            f.write(f"Number of correct triplets: {precision_ai}\n")
            if precision_score_ai is not None:
                f.write(f"Precision score: {precision_score_ai:.2f}\n")
            else:
                f.write("Precision score: N/A\n")

            # computes precision without AI
            text_sentences = extract_sentences_from_text_content(text_content)
            precision_no_ai = compute_precision_fuzzy(text_sentences, triplets, 60)
            if len(triplets) > 0 and precision_no_ai is not None:
                tp = precision_no_ai  # correct triplets
                fp = len(triplets) - tp
                precision_score_no_ai = tp / (tp + fp) if (tp + fp) else 0
            else:
                precision_score_no_ai = None
            f.write(f"Precision with Similarity Test (FuzzyWuzzy Threshold 60)\n")
            f.write(f"Number of correct triplets: {precision_no_ai}\n")
            if precision_score_no_ai is not None:
                f.write(f"Precision score: {precision_score_no_ai:.2f}\n")
            else:
                f.write("Precision score: N/A\n")

            # computes recall with AI
            recall = compute_recall(data[url])
            if len(triplets) > 0 and recall is not None:
                tp = precision_ai  # correct triplets
                fn = recall   # LLM-estimated missing ones
                recall_score = tp / (tp + fn) if (tp + fn) else 0
            else:
                recall_score = None
            f.write(f"Recall with Mistral:7b-Instruct\n")
            f.write(f"Number of triplets that could've been extracted: {recall}\n")
            if recall_score is not None:
                f.write(f"Recall score: {recall_score:.2f}\n")
            else:
                f.write("Recall score: N/A\n")

            # calculates f1 with precision ai
            if precision_score_ai is not None and recall_score is not None:
                f1_ai = 2 * precision_score_ai * recall_score / (precision_score_ai + recall_score) if (precision_score_ai + recall_score) else 0
                f.write(f"F1 with precision AI: {f1_ai:.2f}\n")
            else:
                f.write("F1 with precision AI: N/A\n")

            # calculates f1 with precision no ai
            if precision_score_no_ai is not None and recall_score is not None:
                f1_no_ai = 2 * precision_score_no_ai * recall_score / (precision_score_no_ai + recall_score) if (precision_score_no_ai + recall_score) else 0
                f.write(f"F1 with precision no AI: {f1_no_ai:.2f}\n\n")
            else:
                f.write("F1 with precision no AI: N/A\n\n")

            if precision_score_ai is not None and recall_score is not None:
                total_precision_ai += precision_score_ai
                total_f1_ai += f1_ai
                total_recall += recall_score
                count += 1

            if precision_score_no_ai is not None and recall_score is not None:
                total_precision_fuzzy += precision_score_no_ai
                total_f1_fuzzy += f1_no_ai

    if count > 0:
        avg_precision_ai = total_precision_ai / count
        avg_precision_fuzzy = total_precision_fuzzy / count
        avg_recall = total_recall / count
        avg_f1_ai = total_f1_ai / count
        avg_f1_fuzzy = total_f1_fuzzy / count

        with open("output_file", "a", encoding="utf-8") as f:
            f.write("\n====== Overall Averages (Macro) ======\n")
            f.write(f"Average Precision (AI): {avg_precision_ai:.2f}\n")
            f.write(f"Average Precision (Fuzzy): {avg_precision_fuzzy:.2f}\n")
            f.write(f"Average Recall: {avg_recall:.2f}\n")
            f.write(f"Average F1 (AI): {avg_f1_ai:.2f}\n")
            f.write(f"Average F1 (Fuzzy): {avg_f1_fuzzy:.2f}\n")