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

# ----------------------
#  Ensure templates directory exists
# ----------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

if not os.path.exists(TEMPLATE_DIR):
    os.makedirs(TEMPLATE_DIR)
    print(f"Created missing templates directory: {TEMPLATE_DIR}")

# Initialize Jinja2Templates
templates = Jinja2Templates(directory=TEMPLATE_DIR)

# ----------------------
#  Ensure 'utils' package is found
# ----------------------
sys.path.append(BASE_DIR)

from utils.search import (
    get_text_files_content,
    improved_search_in_repo
)

# ----------------------
#  Initialize FastAPI app
# ----------------------
app = FastAPI()

# ----------------------
#  Load environment variables
# ----------------------
load_dotenv()
DEFAULT_REPO_PATH = os.getenv("REPO_PATH")

if not DEFAULT_REPO_PATH:
    raise EnvironmentError("ERROR: REPO_PATH is not set in .env file!")

# ----------------------
# Load embedding model
# ----------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

# ----------------------
#  Preprocess corpus from a given repo path
# ----------------------
def prepare_corpus(repo_path):
    file_data = get_text_files_content(repo_path)
    corpus = [content for _, content in file_data]
    file_names = [filename for filename, _ in file_data]

    if not corpus:
        raise ValueError("ERROR: No text files found in the repository!")

    corpus_embeddings = model.encode(corpus, convert_to_tensor=False)
    embedding_dim = len(corpus_embeddings[0])
    index = faiss.IndexFlatL2(embedding_dim)
    index.add(np.array(corpus_embeddings))

    return corpus, file_names, index

# Prepare the initial corpus using default path
corpus, file_names, index = prepare_corpus(DEFAULT_REPO_PATH)

# ----------------------
#  Routes
# ----------------------

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    """Render the main search page."""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "repo_path": DEFAULT_REPO_PATH
    })


@app.get("/search")
def search(
    request: Request,
    query: str = Query(...),
    k: int = 100,
    embedding: bool = Query(False),
    repo_path: str = Query(None)
):
    """Search for files using either embedding or keyword search."""
    path_to_use = repo_path or DEFAULT_REPO_PATH
    temp_corpus, temp_files, temp_index = prepare_corpus(path_to_use)
    k = min(k, len(temp_corpus))
    results = []

    if embedding:
        query_embedding = model.encode([query], convert_to_tensor=False)
        query_embedding_np = np.array(query_embedding).reshape(1, -1)
        distances, indices = temp_index.search(query_embedding_np, k)

        results = [
            {
                "file": temp_files[i],
                "snippet": temp_corpus[i][:300],
                "distance": float(d)
            }
            for i, d in zip(indices[0], distances[0])
        ]
    else:
        for i, content in enumerate(temp_corpus):
            match_count = content.lower().count(query.lower())
            if match_count > 0:
                results.append({
                    "file": temp_files[i],
                    "snippet": content[:300],
                    "score": match_count
                })

    return {
        "query": query,
        "repo_path": path_to_use,
        "results": results
    }


@app.get("/advanced_search")
def advanced_search(
    query: str = Query(...),
    search_type: str = Query("combined"),
    repo_path: str = Query(None)
):
    """Perform an advanced search with different strategies."""
    path_to_use = repo_path or DEFAULT_REPO_PATH
    results = improved_search_in_repo(path_to_use, query, search_type)
    return {
        "query": query,
        "search_type": search_type,
        "repo_path": path_to_use,
        "results": results
    }

# ----------------------
# Automatically open browser when the server starts
# ----------------------
def open_browser():
    time.sleep(1)
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    threading.Thread(target=open_browser).start()
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
