from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import numpy as np
import faiss
import os
import threading
import webbrowser
import time

from utils.search import (
    get_text_files_content,
    improved_search_in_repo,
    safe_search,
    get_context
)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Load environment variables
load_dotenv()
repo_path = os.getenv("REPO_PATH")

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load and encode file contents
file_data = get_text_files_content(repo_path)
corpus = [content for _, content in file_data]
file_names = [filename for filename, _ in file_data]
corpus_embeddings = model.encode(corpus, convert_to_tensor=False)

# Setup FAISS index
embedding_dim = len(corpus_embeddings[0])
index = faiss.IndexFlatL2(embedding_dim)
index.add(np.array(corpus_embeddings))

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/search")
def search(query: str = Query(...), k: int = 100, embedding: bool = Query(False)):
    """
    Search for files using either embedding search or keyword search.
    - `embedding` is a boolean query parameter, which if True will perform semantic search.
    """
    k = min(k, len(corpus))  # Limit k to the number of documents
    results = []

    if embedding:
        # Perform embedding-based (semantic) search
        query_embedding = model.encode([query], convert_to_tensor=False)
        query_embedding_np = np.array(query_embedding).reshape(1, -1)
        distances, indices = index.search(query_embedding_np, k)

        results = [
            {
                "file": file_names[i],
                "snippet": corpus[i][:300],
                "distance": float(d)
            }
            for i, d in zip(indices[0], distances[0])
        ]
    else:
        # Perform keyword-based search with scoring (e.g., number of matches or custom score)
        for i, content in enumerate(corpus):
            match_count = content.lower().count(query.lower())  # Count occurrences of the query in the content
            if match_count > 0:
                score = match_count  # Score based on the number of matches (could be customized)
                results.append({
                    "file": file_names[i],
                    "snippet": content[:300],  # Show the first 300 chars as a snippet
                    "score": score  # Use the match count as the score
                })

    return {"query": query, "results": results}

@app.get("/advanced_search")
def advanced_search(query: str = Query(...), search_type: str = Query("combined")):
    results = improved_search_in_repo(repo_path, query, search_type)
    return {"query": query, "search_type": search_type, "results": results}

def open_browser():
    time.sleep(1)
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    threading.Thread(target=open_browser).start()
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
