import os
import ast
import random

UNVALIDATED_FOLDER = "amazon_triplets"
FILENAME = "triplets_1"

VALIDATED_FOLDER = "validated_amazon_triplets"
VALIDATED_FILENAME = f"validated_{FILENAME}.txt"

def validation(triplet):

    triplet = ast.literal_eval(triplet)

    # REPLACE THIS WITH ACTUAL VALIDATION METHOD
    score = round(random.random(), 3)
    
    return score

if __name__ == '__main__':
    validated_triplets = []
    file = os.path.join(UNVALIDATED_FOLDER, FILENAME)
    with open(file, "r") as f:
        triplets = f.readlines()

    for triplet in triplets:
        triplet = triplet.strip()
        score = validation(triplet)
        validated_triplets.append(f"{triplet} {score}")
    
    new_file = os.path.join(VALIDATED_FOLDER, VALIDATED_FILENAME)

    with open(new_file, "w") as f:
        for triplet in validated_triplets:
            f.write(triplet)
            f.write("\n")
