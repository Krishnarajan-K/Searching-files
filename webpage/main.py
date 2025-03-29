import os
import json
from dotenv import load_dotenv
from utils.search import get_text_files_content
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

def main():
    # Load environment variables from .env
    load_dotenv()
    repo_path = os.getenv("REPO_PATH")

    if not repo_path or not os.path.isdir(repo_path):
        print("Repository path is not valid or not found in .env file.")
        return

    # Load files and extract text content
    file_data = get_text_files_content(repo_path)  # Returns list of (filename, content)
    if not file_data:
        print("No text files found in the repository.")
        return

    corpus = [content for _, content in file_data]
    file_names = [filename for filename, _ in file_data]

    # Load the sentence transformer model
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Encode corpus
    corpus_embeddings = model.encode(corpus, convert_to_tensor=False)
    corpus_embeddings_np = np.array(corpus_embeddings)

    # Build FAISS index
    embedding_dim = corpus_embeddings_np.shape[1]
    index = faiss.IndexFlatL2(embedding_dim)
    index.add(corpus_embeddings_np)

    # Ask for user query
    query = input("Enter your semantic search query: ").strip()
    if not query:
        print("Query cannot be empty.")
        return

    # Encode the query
    query_embedding = model.encode([query], convert_to_tensor=False)
    query_embedding_np = np.array(query_embedding).reshape(1, -1)

    # Search in index
    k = 3
    distances, indices = index.search(query_embedding_np, k)

    print("\nTop Matches:")
    for rank, (i, d) in enumerate(zip(indices[0], distances[0]), 1):
        print(f"{rank}. File: {file_names[i]}")
        print(f"   Snippet: {corpus[i][:200].strip().replace('\n', ' ')}...")
        print(f"   Distance: {d:.4f}\n")

    # Optional: Save results
    write_to_file = input("Write top results to output.json? (yes/no): ").strip().lower() == 'yes'
    if write_to_file:
        output_data = [
            {"file": file_names[i], "snippet": corpus[i][:500], "distance": float(d)}
            for i, d in zip(indices[0], distances[0])
        ]
        try:
            with open("output.json", "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=4)
            print("Results saved to output.json")
        except Exception as e:
            print(f"Error writing to file: {e}")

if __name__ == "__main__":
    main()
