import os
import shutil

# Configure source directory and destination parent directory
source_dir = "amazon_htmls"  # Change this to your directory
dest_dir = "amazon_batches"  # Change this to where folders should be created

batch_size = 80

def batch_files(source, destination, batch_size):
    files = [f for f in os.listdir(source) if os.path.isfile(os.path.join(source, f))]
    total_files = len(files)
    num_batches = (total_files // batch_size) + (1 if total_files % batch_size else 0)

    for batch_num in range(num_batches):
        batch_folder = os.path.join(destination, f"batch_{batch_num + 1}")
        os.makedirs(batch_folder, exist_ok=True)

        start_index = batch_num * batch_size
        end_index = min(start_index + batch_size, total_files)
        batch_files = files[start_index:end_index]

        for file in batch_files:
            shutil.move(os.path.join(source, file), os.path.join(batch_folder, file))

        print(f"Moved {len(batch_files)} files to {batch_folder}")

if __name__ == "__main__":
    batch_files(source_dir, dest_dir, batch_size)
