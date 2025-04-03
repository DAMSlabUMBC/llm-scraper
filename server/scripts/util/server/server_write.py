def server_write_files(sftp, remote_file_path, text):
    """
    Writes text content to a remote file via SFTP.

    Args:
        sftp (paramiko.SFTPClient): The active SFTP client.
        remote_file_path (str): The full remote path to the file.
        text (str): The text content to write.
    """
    try:
        with sftp.open(remote_file_path, 'w') as remote_file:
            remote_file.write(text)
        print(f"Successfully wrote to {remote_file_path}")
    except Exception as e:
        print(f"Error writing to remote file {remote_file_path}: {e}")
