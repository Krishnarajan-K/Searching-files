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

from utils.search import get_text_files_content  # Your utility function to read text files

# Initialize FastAPI and templates
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

# Route to serve index.html
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Search endpoint
@app.get("/search")
def search(query: str = Query(...), k: int = 100):
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
    return {"query": query, "results": results}

# Auto-open browser when server starts
def open_browser():
    time.sleep(1)  # Delay to wait for the server to start
    webbrowser.open("http://127.0.0.1:8000")

# Main entry point to run with auto-browser
if __name__ == "__main__":
    threading.Thread(target=open_browser).start()
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
