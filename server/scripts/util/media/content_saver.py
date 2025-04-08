import os

def save_content(subfolders, content, content_type, extension="txt"):
    folder = subfolders[content_type]
    file_path = os.path.join(folder, f"{content_type}_content.{extension}")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def save_links(folder, links, filename):
    """Save links to a specified file in the links folder."""
    file_path = os.path.join(folder, filename)
    with open(file_path, 'w') as f:
        for link in links:
            f.write(f"{link}\n")
