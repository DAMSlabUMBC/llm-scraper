import os

ALL_URLS = "official_best_buy_urls.txt" #"bestbuy_urls.txt" #"official_best_buy_urls.txt"
FOLDER = "bestbuy_batches"
BATCH_SIZE = 200
TEMP_URLS = "official_best_buy_urls.txt"

def batch_urls(start=0):
    # Make sure the output folder exists
    os.makedirs(FOLDER, exist_ok=True)

    # Read all URLs
    with open(ALL_URLS, "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    # Create batches
    for i in range(0, len(urls), BATCH_SIZE):
        batch = urls[i:i + BATCH_SIZE]
        batch_file = os.path.join(FOLDER, f"batch_{start+i // BATCH_SIZE + 1}.txt")
        with open(batch_file, "w") as f:
            f.write("\n".join(batch))

    print(f"✅ Created {len(urls) // BATCH_SIZE + (1 if len(urls) % BATCH_SIZE != 0 else 0)} batch files in '{FOLDER}'")

def rebatch(start, end):
    with open(TEMP_URLS, "a") as f:
        for i in range (start, end):
            
            with open(os.path.join(FOLDER, f"batch_{i}.txt"), "r") as g:
                urls = g.readlines()

            for url in urls:
                f.write(url)

            
            # Check if the file exists before deleting
            if os.path.exists(os.path.join(FOLDER, f"batch_{i}.txt")):
                os.remove(os.path.join(FOLDER, f"batch_{i}.txt"))
                print(f"batch_{i}.txt has been deleted.")
            else:
                print(f"batch_{i}.txt does not exist")


if __name__ == "__main__":
    # empties temp urls
    with open("bestbuy_urls.txt", "w") as f:
        print("emptying urls")
    #rebatch(1, 26)
    batch_urls()