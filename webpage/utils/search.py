import os

def get_text_files_content(repo_path):
    text_data = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith((".txt", ".py", ".md", ".json")):
                try:
                    with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                        content = f.read()
                        text_data.append((file, content))
                except Exception as e:
                    print(f"Failed to read {file}: {e}")
    return text_data
