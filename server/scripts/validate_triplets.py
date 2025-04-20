import os
import ast

UNVALIDATED_FOLDER = "amazon_triplets"
FILENAME = "triplets_1"
VALIDATED_FOLDER = "validated_amazon_triplets"
VALIDATED_FILENAME = f"validated_{FILENAME}.txt"

if __name__ == "__main__":
    # Read & parse triplets
    raw_path = os.path.join(UNVALIDATED_FOLDER, FILENAME)
    result_list = []
    with open(raw_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # turn the string "(a, b, c)" into a tuple
            result_list.append(ast.literal_eval(line))

    # Attach a default weight of 0.5
    triplets_list = []
    for triplet in result_list:
        default_weight = 0.5
        # triplet is e.g. ('device','Alexa','manufacturer','Amazon')
        # this makes it ('device','Alexa','manufacturer','Amazon', 0.5)
        weighted = triplet + (default_weight,)
        triplets_list.append(weighted)

    # Write to validated folder
    output_path = os.path.join(VALIDATED_FOLDER, VALIDATED_FILENAME)
    os.makedirs(VALIDATED_FOLDER, exist_ok=True)
    with open(output_path, "w") as out:
        for trip in triplets_list:
            out.write(str(trip))
            out.write("\n")
