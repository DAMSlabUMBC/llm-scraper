import os

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

if __name__ == "__main__":

    # opens the file for extracted content
    with open(os.path.join("extracted_samsclub", "batch_1.txt"), "r") as f:
        extracted_lines = [line.strip() for line in f.readlines()]
    
    # opens the file for triplets
    with open(os.path.join("new_samsclub_triplets", "triplets_1.txt"), "r") as f:
        triplets_lines = [line.strip() for line in f.readlines()]

    data = map_content_with_triplets(extracted_lines, triplets_lines)

    with open("preprocessed_precision_recall.txt", "w") as f:
        for url in data:
            f.write(f"{url} {str(data[url])}\n")