import sys
import os
import threading
import time
import webbrowser
import numpy as np
import faiss
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sentence_transformers import SentenceTransformer

# Ensure the 'utils' package can be found
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from utils.search import (
    get_text_files_content,
    improved_search_in_repo,
    safe_search,
    get_context
)

# Initialize FastAPI app
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
    """Search for files using either embedding search or keyword search."""
    k = min(k, len(corpus))  # Limit k to the number of documents
    results = []

    if embedding:
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
        # Perform keyword-based search
        for i, content in enumerate(corpus):
            match_count = content.lower().count(query.lower())
            if match_count > 0:
                results.append({
                    "file": file_names[i],
                    "snippet": content[:300],
                    "score": match_count
                })

    return {"query": query, "results": results}

@app.get("/advanced_search")
def advanced_search(query: str = Query(...), search_type: str = Query("combined")):
    """Perform an advanced search with different strategies."""
    results = improved_search_in_repo(repo_path, query, search_type)
    return {"query": query, "search_type": search_type, "results": results}

# Automatically open browser when the server starts
def open_browser():
    time.sleep(1)
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    threading.Thread(target=open_browser).start()
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
