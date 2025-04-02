import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# 1. Load pre-trained embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# 2. Define your corpus (could also be loaded from a file or DB)
corpus = [
    "How do I use FAISS for semantic search?",
    "What is the capital of France?",
    "How to bake a chocolate cake?",
    "Tell me about machine learning algorithms.",
    "Benefits of daily meditation and mindfulness."
]

# 3. Generate vector embeddings for the corpus
corpus_embeddings = model.encode(corpus, convert_to_tensor=False)
corpus_embeddings_np = np.array(corpus_embeddings)

# 4. Build FAISS index using L2 distance (Euclidean)
embedding_dimension = corpus_embeddings_np.shape[1]
index = faiss.IndexFlatL2(embedding_dimension)
index.add(corpus_embeddings_np)

# 5. Get input from user
query = input("Enter your search query: ")

# 6. Embed the user query
query_embedding = model.encode([query], convert_to_tensor=False)
query_embedding_np = np.array(query_embedding).reshape(1, -1)

# 7. Perform FAISS search
k = 1  # You can increase to return more matches
distances, indices = index.search(query_embedding_np, k)

# 8. Show result
top_match_index = indices[0][0]
print(f"\nTop match: {corpus[top_match_index]}")
print(f"Distance: {distances[0][0]:.4f}")
