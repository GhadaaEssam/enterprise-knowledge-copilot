import json
import pickle
import numpy as np
from pathlib import Path

from src.ingestion.embedder import Embedder
from src.retrieval.text_search import build_minsearch_index
from src.retrieval.search_engines import KeywordSearchEngine, VectorSearchEngine, HybridSearchEngine, SqliteVectorSearchEngine
from src.retrieval.vector_search import VectorSearchIndex
from src.rag.pipeline import RAGPipeline

# 1. Load Data
ROOT = Path(__file__).resolve().parent
with open(ROOT / "data/processed/chunked_documents.json", "r") as f:
    chunks = json.load(f)

embeddings = np.load(ROOT / "data/processed/embeddings.npy")
with open(ROOT / "data/processed/embedding_metadata.pkl", "rb") as f:
    metadata = pickle.load(f)

# 2. Initialize Embedder & Engines
embedder = Embedder(path=ROOT / "src/ingestion/models/Xenova/all-MiniLM-L6-v2")

minsearch_idx = build_minsearch_index(chunks)
keyword_engine = KeywordSearchEngine(minsearch_idx)
vector_engine = VectorSearchEngine(embedder, embeddings, metadata)

# 3. Build RRF Hybrid Engine
hybrid_engine = HybridSearchEngine(keyword_engine, vector_engine, k=60)

# 4. Initialize RAG Pipeline with Hybrid Search Engine
# rag = RAGPipeline(search_engine=hybrid_engine, llm_client=your_llm_client)
# answer = rag.ask("How do we handle production deployments?")