import os

def search_string_in_repo(repo_path, search_string):
    """Search for a string in all files under the repo path."""
    matching_files = []

    for root, dirs, files in os.walk(repo_path):
        for filename in files:
            file_path = os.path.join(root, filename)

            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    if search_string.lower() in content.lower():  # Case-insensitive match
                        matching_files.append(file_path)
            except (UnicodeDecodeError, PermissionError, FileNotFoundError):
                # Skip files that can't be read
                continue

    return matching_files
