import paramiko
import os
from dotenv import load_dotenv
load_dotenv()  

def create_sftp_client(host, port, username, password):
    # Create a transport object and connect to the server
    transport = paramiko.Transport((host, port))
    transport.connect(username=username, password=password)
    
    # Create an SFTP client from the transport
    sftp = paramiko.SFTPClient.from_transport(transport)
    return sftp, transport

def read_files_in_batches(sftp, remote_dest_dir):
    print(f"Reading files from remote directory: {remote_dest_dir}")
    try:
        # List items in the base remote directory (should be batch folders)
        batch_folders = sftp.listdir(remote_dest_dir)
    except Exception as e:
        print(f"Error listing remote directory {remote_dest_dir}: {e}")
        return

    # Process each batch folder (sorting for predictable order)
    for folder in sorted(batch_folders):
        remote_batch_folder = os.path.join(remote_dest_dir, folder)
        print(f"\n--- Reading files in batch folder: {remote_batch_folder} ---")
        try:
            files = sftp.listdir(remote_batch_folder)
        except Exception as e:
            print(f"Error listing folder {remote_batch_folder}: {e}")
            continue

        # Process each file in the batch folder
        for file in files:
            remote_file_path = os.path.join(remote_batch_folder, file)
            try:
                with sftp.open(remote_file_path, 'r') as remote_file:
                    # Read the file content. If the files are text files,
                    # this should work fine. For binary files, you may need to
                    # handle decoding accordingly.
                    content = remote_file.read()
                    print(f"\nContents of {remote_file_path}:\n{content}\n")
            except Exception as e:
                print(f"Error reading file {remote_file_path}: {e}")

def ensure_remote_directory(sftp, remote_directory):
    """
    Recursively create remote directories if they don't exist.
    """
    # Normalize the path and split into parts
    dirs = remote_directory.strip('/').split('/')
    current_path = '/'
    for d in dirs:
        current_path = os.path.join(current_path, d)
        try:
            sftp.stat(current_path)
        except FileNotFoundError:
            sftp.mkdir(current_path)
            print(f"Created remote directory: {current_path}")

if __name__ == "__main__":
    # Configuration
    host = os.getenv("HOST_URL")          # Replace with your server address
    port = 22                            # Default SFTP port)
    username = os.getenv("USERNAME")                  # Your server username
    password = os.getenv("PASSWORD")                 # Your server password
    source_dir = "amazon_htmls"          # Local directory with files
    remote_dest_dir = f"/home/{username}/amazon_batches"  # Remote directory to store batches
    batch_size = 1
    print(host, username, password, remote_dest_dir)

    # Create the SFTP connection
    sftp, transport = create_sftp_client(host, port, username, password)

    try:
        # Ensure the base remote directory exists
        ensure_remote_directory(sftp, remote_dest_dir)

        # Read files in batches
        read_files_in_batches(sftp, remote_dest_dir)
    finally:
        # Always close the connection
        sftp.close()
        transport.close()
