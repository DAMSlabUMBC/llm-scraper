import os
import ollama
import torch
import re
import ast
from fuzzywuzzy import fuzz
from tqdm import tqdm
import argparse

RETRIES = 3
TRIPLET_PATTERN = r"""
\(\(\s*['"]([^'"]+)['"]\s*,\s*['"]([^'"]+)['"]\s*\)\s*,     # Subject
\s*['"]([^'"]+)['"]\s*,                                     # Predicate
\s*\(\s*['"]([^'"]+)['"]\s*,\s*['"]([^'"]+)['"]\s*\)\)       # Object
"""

def normalize_string(s):
    if not isinstance(s, str):
        s = str(s)
    s = s.lower()
    s = re.sub(r'[\W_]+', '', s)  # remove all non-alphanumeric characters
    return s.strip()

def normalize_triplet(triplet):
    (subj_type, subj_ent), predicate, (obj_type, obj_ent) = triplet
    return (
        (normalize_string(subj_type), normalize_string(subj_ent)),
        normalize_string(predicate),
        (normalize_string(obj_type), normalize_string(obj_ent)),
    )

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

def clean_triplets(triplets):
    cleaned_triplets = []
    for triplet_str in triplets:
        try:
            triplet = ast.literal_eval(triplet_str)
            
            # step 2: optionally normalize entity names
            subj_type, subj_name = triplet[0]
            pred = triplet[1]
            obj_type, obj_name = triplet[2]

            # insert spaces between camel case or joined words, for readability
            subj_name = re.sub(r'(?<!\s)([A-Z])', r' \1', subj_name).replace('"', '" ')
            obj_name = re.sub(r'(?<!\s)([A-Z])', r' \1', obj_name)

            # replace camelCase artifacts like "Anti-glaretechnology"
            subj_name = re.sub(r'([a-z])([A-Z])', r'\1 \2', subj_name)
            obj_name = re.sub(r'([a-z])([A-Z])', r'\1 \2', obj_name)

            # remove extra spaces
            subj_name = ' '.join(subj_name.split())
            obj_name = ' '.join(obj_name.split())

            cleaned_triplets.append(((subj_type, subj_name), pred, (obj_type, obj_name)))
        except Exception as e:
            print(f"Failed to parse: {triplet_str}\nError: {e}")

    return cleaned_triplets

def compute_precision(combined_input, triplets):

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
                    You will be given a product description and a list of triplets.

                    Each triplet is in the format:
                    (('type1', 'entity1'), 'relationship', ('type2', 'entity2'))

                    Your task is to return **only** the triplets that are fully and explicitly supported by the product description.

                    A triplet is correct **only if all three components are clearly stated** in the product description — no assumptions, no guesses.

                    ---

                    🛑 Output Rules:
                    - Return only the correct triplets as a Python-style list of tuples.
                    - Do NOT include any explanation, labels, or extra text.
                    - If no triplets are correct, return an empty list: `[]`

                    ---

                    ✅ Example Input:
                    {
                    "text_content": {
                    "product_name": "Amazon Echo Dot",
                    "description": "Smart speaker with Alexa. Connects via Wi-Fi and Bluetooth. Supports smart home control."
                    },
                    "triplets": [
                    (("device", "Amazon Echo Dot"), "compatibleWith", ("application", "Alexa")),
                    (("device", "Amazon Echo Dot"), "hasFeature", ("feature", "Bluetooth")),
                    (("device", "Amazon Echo Dot"), "connectsTo", ("protocol", "Z-Wave"))
                    ]
                    }

                    ✅ Example Output:
                    [
                    (("device", "Amazon Echo Dot"), "compatibleWith", ("application", "Alexa")),
                    (("device", "Amazon Echo Dot"), "hasFeature", ("feature", "Bluetooth"))
                    ]

                    ---

                    Now do the same for:
                    {your_combined_input_here}
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

        print(f"PRECISION AI: {precision}")

        parsed_response = ast.literal_eval(precision)
        
        if not isinstance(parsed_response, str):
            parsed_response = re.findall(TRIPLET_PATTERN, parsed_response, flags=re.VERBOSE)

        cleaned_triplets = []
        for t in parsed_response:
            if (
                isinstance(t, tuple) and len(t) == 3 and
                isinstance(t[0], tuple) and isinstance(t[2], tuple) and
                len(t[0]) == 2 and len(t[2]) == 2
            ):
                cleaned_triplets.append(normalize_triplet(t))
        
        # then check for no duplicates triplets
        cleaned_triplets = list(set(cleaned_triplets))

        if cleaned_triplets:
            print(f"Cleaned triplets: {cleaned_triplets}")
            print(f"Extracted triplets: {triplets}")
        else:
            print("Cleaned triplets are empty")

        
        # normalize triplets and count matches
        normalized_input = [normalize_triplet(t) for t in triplets]  # from input param
        matched_triplets = [t for t in cleaned_triplets if t in normalized_input]

        # returns the number of matched triplets found
        if matched_triplets:
            print(f"Total generated: {len(cleaned_triplets)}, Found: {len(matched_triplets)}")
            return len(matched_triplets)
        
    print("Unable to parse triplets")
    return None

def compute_recall(combined_input, triplets):

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
                    You will be given a product description and a list of extracted triplets.

                    Each triplet is in the format:
                    (('type1', 'entity1'), 'relationship', ('type2', 'entity2'))

                    Your task is to generate **additional valid triplets** that could have been extracted from the product description, **but are not included** in the given triplet list.

                    A valid triplet must be explicitly and clearly supported by the product information.

                    ---

                    🛑 Output Rules:
                    - Return only the **additional** valid triplets as a Python-style list of tuples.
                    - Do NOT include any explanation, labels, or extra text.
                    - If there are no additional valid triplets, return an empty list: `[]`
                    - Do NOT return duplicates of the input triplets.

                    ---

                    ✅ Example Input:
                    {
                    "text_content": {
                    "product_name": "Amazon Echo Dot",
                    "features": "Smart speaker with Alexa. Supports voice commands, Wi-Fi, and Bluetooth. Compatible with smart home devices."
                    },
                    "triplets": [
                    (("device", "Amazon Echo Dot"), "compatibleWith", ("application", "Alexa")),
                    (("device", "Amazon Echo Dot"), "hasFeature", ("feature", "Voice Commands"))
                    ]
                    }

                    ✅ Example Output:
                    [
                    (("device", "Amazon Echo Dot"), "supportsProtocol", ("protocol", "Wi-Fi")),
                    (("device", "Amazon Echo Dot"), "supportsProtocol", ("protocol", "Bluetooth")),
                    (("device", "Amazon Echo Dot"), "isCategory", ("category", "Smart Speaker"))
                    ]

                    ---

                    Now generate additional valid triplets for:
                    {your_combined_input}
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

        print(f"RECALL AI: {recall}")

        try:
            parsed_response = ast.literal_eval(recall)
        except Exception as e:
            continue

        cleaned_triplets = []
        for t in parsed_response:
            if (
                isinstance(t, tuple) and len(t) == 3 and
                isinstance(t[0], tuple) and isinstance(t[2], tuple) and
                len(t[0]) == 2 and len(t[2]) == 2
            ):
                cleaned_triplets.append(normalize_triplet(t))
        
        # parse out all the triplets generated in the response
        # generated_triplets = re.findall(TRIPLET_PATTERN, recall)

        # print(f"GENERATED TRIPLETS: {generated_triplets}")

        # cleaned_triplets = []
        # for triplet_str in generated_triplets:
        #     try:
        #         t = ast.literal_eval(triplet_str.replace("‘", "'").replace("’", "'"))
        #         if isinstance(t, tuple) and len(t) == 3:
        #             if isinstance(t[0], tuple) and isinstance(t[2], tuple):
        #                 if len(t[0]) == 2 and len(t[2]) == 2:
        #                     cleaned_triplets.append(normalize_triplet(t))
        #     except Exception as e:
        #         pass

        
        # then check for no duplicates triplets
        cleaned_triplets = list(set(cleaned_triplets))

        if cleaned_triplets:
            print(f"Cleaned triplets: {cleaned_triplets}")
            print(f"Extracted triplets: {triplets}")
        else:
            print("Cleaned triplets are empty")

        # normalize triplets and count matches
        normalized_input = [normalize_triplet(t) for t in triplets]  # from input param
        remaining_triplets = [t for t in cleaned_triplets if t not in normalized_input]

        # returns length of generated triplets
        if remaining_triplets:
            print(f"Total generated: {len(cleaned_triplets)}, Missed: {len(remaining_triplets)}")
            return len(remaining_triplets)
        
    print("Unable to parse triplets")
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
    triplets = str_triplets

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
    parser.add_argument("--ollama_port", type=int, help="Port number for Ollama")

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

    exit()

    # iterates through each product to calculate precision and recall
    with open(output_file, "w", encoding="utf-8") as f:
        for url in tqdm(data):
            print(f"URL: {url}")
            text_content = data[url]["text_content"]
            triplets = data[url]["triplets"]

            #print(f"triplets before: {triplets}")

            # cleans the triplets
            triplets = clean_triplets(triplets)

            # print(f"triplets after: {triplets}")

            # for triplet in triplets:
            #     print(type(triplet))


            # computes precision with AI
            if triplets:  # non-empty list evaluates to True
                precision_ai = compute_precision(data[url], triplets)
            else:
                precision_ai = 0  # or None, depending on how you want to handle it

            if len(triplets) > 0 and precision_ai is not None:
                tp = precision_ai  # correct triplets
                fp = len(triplets) - tp
                precision_score_ai = tp / (tp + fp) if (tp + fp) else 0
            else:
                precision_score_ai = 0
            f.write(f"URL: {url}\n")
            f.write(f"Text content: {text_content}\n")
            f.write(f"Extracted triplets: {triplets}\n")
            f.write(f"Number of extracted triplets: {len(triplets)}\n")
            f.write(f"Precision with Mistral:7b-Instruct\n")
            f.write(f"Number of correct triplets: {precision_ai}\n")
            if precision_score_ai is not None:
                f.write(f"Precision score: {precision_score_ai:.2f}\n")
            else:
                f.write("Precision score: N/A\n")

            # computes precision without AI
            text_sentences = extract_sentences_from_text_content(text_content)
            if data[url]["triplets"]:  # non-empty list evaluates to True
                precision_no_ai = compute_precision_fuzzy(text_sentences, triplets, 60)
            else:
                precision_no_ai = 0  # or None, depending on how you want to handle it

            if len(triplets) > 0 and precision_no_ai is not None:
                tp = precision_no_ai  # correct triplets
                fp = len(triplets) - tp
                precision_score_no_ai = tp / (tp + fp) if (tp + fp) else 0
            else:
                precision_score_no_ai = 0
            f.write(f"Precision with Similarity Test (FuzzyWuzzy Threshold 60)\n")
            f.write(f"Number of correct triplets: {precision_no_ai}\n")
            if precision_score_no_ai is not None:
                f.write(f"Precision score: {precision_score_no_ai:.2f}\n")
            else:
                f.write("Precision score: N/A\n")

            # computes recall with precision AI
            recall = compute_recall(data[url], triplets)
            if precision_ai is not None and recall is not None:
                tp = precision_ai  # correct triplets
                fn = recall   # LLM-estimated missing ones
                recall_score_ai = tp / (tp + fn) if (tp + fn) else 0
            else:
                recall_score_ai = None
            f.write(f"Recall with Precision Mistral:7b-Instruct\n")
            f.write(f"Number of triplets that could've been extracted: {recall}\n")
            if recall_score_ai is not None:
                f.write(f"Recall score: {recall_score_ai:.2f}\n")
            else:
                f.write("Recall score: N/A\n")

            # computes recall with precision no AI
            if precision_no_ai is not None and recall is not None:
                tp = precision_no_ai  # correct triplets
                fn = recall   # LLM-estimated missing ones
                recall_score_no_ai = tp / (tp + fn) if (tp + fn) else 0
            else:
                recall_score_no_ai = None
            f.write(f"Recall with Precision no AI\n")
            if recall_score_no_ai is not None:
                f.write(f"Recall score: {recall_score_no_ai:.2f}\n")
            else:
                f.write("Recall score: N/A\n")

            # calculates f1 with precision ai
            if precision_score_ai is not None and recall_score_ai is not None:
                f1_ai = 2 * precision_score_ai * recall_score_ai / (precision_score_ai + recall_score_ai) if (precision_score_ai + recall_score_ai) else 0
                f.write(f"F1 with precision AI: {f1_ai:.2f}\n")
            else:
                f.write("F1 with precision AI: N/A\n")

            # calculates f1 with precision no ai
            if precision_score_no_ai is not None and recall_score_no_ai is not None:
                f1_no_ai = 2 * precision_score_no_ai * recall_score_no_ai / (precision_score_no_ai + recall_score_no_ai) if (precision_score_no_ai + recall_score_no_ai) else 0
                f.write(f"F1 with precision no AI: {f1_no_ai:.2f}\n\n")
            else:
                f.write("F1 with precision no AI: N/A\n\n")

            if precision_score_ai is not None and recall_score_ai is not None:
                total_precision_ai += precision_score_ai
                total_f1_ai += f1_ai
                total_recall += recall_score_ai
                count += 1

            if precision_score_no_ai is not None and recall_score_no_ai is not None:
                total_precision_fuzzy += precision_score_no_ai
                total_f1_fuzzy += f1_no_ai

    if count > 0:
        avg_precision_ai = total_precision_ai / count
        avg_precision_fuzzy = total_precision_fuzzy / count
        avg_recall = total_recall / count
        avg_f1_ai = total_f1_ai / count
        avg_f1_fuzzy = total_f1_fuzzy / count

        with open(output_file, "a", encoding="utf-8") as f:
            f.write("\n====== Overall Averages (Macro) ======\n")
            f.write(f"Average Precision (AI): {avg_precision_ai:.2f}\n")
            f.write(f"Average Precision (Fuzzy): {avg_precision_fuzzy:.2f}\n")
            f.write(f"Average Recall: {avg_recall:.2f}\n")
            f.write(f"Average F1 (AI): {avg_f1_ai:.2f}\n")
            f.write(f"Average F1 (Fuzzy): {avg_f1_fuzzy:.2f}\n")