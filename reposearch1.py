import os

def search_string_in_repo(repo_path, search_string):
    matching_files = []

    for root, dirs, files in os.walk(repo_path):
        for filename in files:
            file_path = os.path.join(root, filename)

            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    if search_string in content:
                        matching_files.append(filename)  
            except (UnicodeDecodeError, PermissionError, FileNotFoundError):
                continue

    return matching_files

if __name__ == "__main__":
    repo_path = input("Enter the path to the repository folder: ").strip()
    search_string = input("Enter the string to search: ").strip()

    result = search_string_in_repo(repo_path, search_string)

    if result:
        print(f"\nFiles containing the string '{search_string}':")
        for filename in set(result):  
            print(f"- {filename}")
    else:
        print(f"\nNo files found containing the string '{search_string}'.")
