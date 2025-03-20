import os
from dotenv import load_dotenv

# Load environment variables from .env file.
load_dotenv()

def list_files_in_folder(folder_path):
    """Returns a list of files in the given folder."""
    try:
        return [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    except FileNotFoundError:
        print(f"Error: Folder '{folder_path}' not found.")
        return []
    except PermissionError:
        print(f"Error: Permission denied to access '{folder_path}'.")
        return []

def calculate_suitability_score(file_name, search_text):
    """Calculates a score based on how well the filename matches the search text."""
    file_name_lower = file_name.lower()
    search_text_lower = search_text.lower()

    if file_name_lower == search_text_lower + ".txt": 
        score = 100
        occurrence = 1  
    elif file_name_lower.startswith(search_text_lower):  
        score = 95
        occurrence = 1  
    elif search_text_lower in file_name_lower:  
        score = 90 + file_name_lower.count(search_text_lower) * 5
        occurrence = 0  
    else:
        score = 0
        occurrence = 0  

    return score, occurrence

if __name__ == "__main__":
    # Get the folder path from environment variable
    folder_path = os.getenv('FOLDER_PATH')
    
    if not folder_path:
        print("Error: Folder path is not set in the .env file.")
    else:
        search_text = input("Enter text to search for in filenames: ").strip().lower()

        files = list_files_in_folder(folder_path)

        if not files:
            print("\nNo files found in the folder.")
        else:
            print(f"\nSearching filenames for: '{search_text}'\n")

            file_scores = {file: calculate_suitability_score(file, search_text) for file in files}

            sorted_files = sorted(file_scores.items(), key=lambda x: (-x[1][0], -x[1][1], x[0]))

            print(" **Sorted by Suitability & Occurrences:**\n")
            for file, (score, occurrences) in sorted_files:
                print(f" {file} | | Occurrences: {occurrences}")
