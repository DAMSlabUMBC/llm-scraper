import os

# Set the folder path
folder_path = 'amazon_htmls'  # <-- Change this

# Get a list of files (excluding directories)
files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

# Sort files for consistency
files.sort()

# Loop through and rename
for i, filename in enumerate(files, start=5000):
    file_ext = os.path.splitext(filename)[1]  # Get the file extension
    new_name = f"amazon{i}{file_ext}"
    src = os.path.join(folder_path, filename)
    dst = os.path.join(folder_path, new_name)
    os.rename(src, dst)
    print(f"Renamed: {filename} -> {new_name}")
