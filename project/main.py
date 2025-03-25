import os
import json
from dotenv import load_dotenv
from utils.search import search_string_in_repo

def main():
    # Load environment variables from .env file
    load_dotenv()
    repo_path = os.getenv("REPO_PATH")

    if not repo_path:
        print("Repository path not found in .env file.")
        return

    # Get user input
    search_string = input("Enter the string to search: ").strip()
    write_to_file = input("Write results to output.json? (yes/no): ").strip().lower() == 'yes'

    # Perform the search
    result = search_string_in_repo(repo_path, search_string)

    # Display or save results
    if result:
        print(f"\nFiles containing the string '{search_string}':")
        file_names = sorted({os.path.basename(path) for path in result})
        for filename in file_names:
            print(f"- {filename}")

        if write_to_file:
            with open("output.json", "w", encoding="utf-8") as f:
                json.dump(file_names, f, indent=4)
            print("\nResults written to output.json")
    else:
        print(f"\nNo files found containing the string '{search_string}'.")

if __name__ == "__main__":
    main()
