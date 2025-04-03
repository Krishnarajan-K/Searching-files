import os
import logging
from multiprocessing import Pool
from sentence_transformers import SentenceTransformer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ==============================
# Basic Content Loader
# ==============================

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

# ==============================
# Core Search Functionality
# ==============================

def improved_search_in_repo(repo_path, search_string, search_type="combined"):
    matching_files = []

    if search_type in ["semantic", "combined"]:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        query_embedding = model.encode([search_string], convert_to_tensor=False)

    for root, _, files in os.walk(repo_path):
        for filename in files:
            file_path = os.path.join(root, filename)

            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    score = 0

                    if search_type in ["text", "combined"]:
                        if search_string.lower() in content.lower():
                            score = 1

                    if search_type in ["semantic", "combined"]:
                        content_embedding = model.encode([content], convert_to_tensor=False)
                        semantic_score = calculate_similarity(query_embedding, content_embedding)
                        score += semantic_score

                    if score > 0:
                        matching_files.append({
                            'path': file_path,
                            'score': score
                        })
            except (UnicodeDecodeError, PermissionError, FileNotFoundError):
                continue

    return sorted(matching_files, key=lambda x: x['score'], reverse=True)

def parallel_search(repo_path, search_string, num_processes=4):
    all_files = []
    for root, _, files in os.walk(repo_path):
        all_files.extend([os.path.join(root, f) for f in files])

    with Pool(num_processes) as pool:
        args = [(f, search_string) for f in all_files]
        results = pool.map(process_file, args)

    return [r for r in results if r is not None]

def search_generator(repo_path, search_string):
    for root, _, files in os.walk(repo_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    for line in file:
                        if search_string.lower() in line.lower():
                            yield {
                                'path': file_path,
                                'line': line.strip()
                            }
                            break
            except:
                continue

# ==============================
# Helpers
# ==============================

def process_file(args):
    file_path, search_string = args
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            if search_string.lower() in content.lower():
                return file_path
    except:
        return None

def is_valid_file(filename, allowed_extensions=None):
    if not allowed_extensions:
        return True
    return any(filename.endswith(ext) for ext in allowed_extensions)

def get_context(file_path, search_string, context_lines=2):
    matches = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if search_string.lower() in line.lower():
                    start = max(0, i - context_lines)
                    end = min(len(lines), i + context_lines + 1)
                    context = ''.join(lines[start:end])
                    matches.append({
                        'line_number': i + 1,
                        'context': context
                    })
    except:
        pass
    return matches

def calculate_relevance_score(file_path, search_string, content):
    score = 0
    if search_string.lower() in content.lower():
        score += 10
    if search_string.lower() in os.path.basename(file_path).lower():
        score += 5
    score += content.lower().count(search_string.lower())
    try:
        score += get_file_recency_score(file_path)
    except:
        pass
    return score

def calculate_similarity(query_embedding, content_embedding):
    import numpy as np
    return float(np.dot(query_embedding, content_embedding[0]) / (np.linalg.norm(query_embedding) * np.linalg.norm(content_embedding[0])))

def get_file_recency_score(file_path):
    import time
    last_modified = os.path.getmtime(file_path)
    current_time = time.time()
    age_in_days = (current_time - last_modified) / (60 * 60 * 24)
    return max(0, 30 - int(age_in_days))

# ==============================
# Safe / Logging Wrapper
# ==============================

def safe_search(repo_path, search_string):
    try:
        results = parallel_search(repo_path, search_string)
        logging.info(f"Search completed successfully. Found {len(results)} matches.")
        return results
    except Exception as e:
        logging.error(f"Search failed: {str(e)}")
        return []
