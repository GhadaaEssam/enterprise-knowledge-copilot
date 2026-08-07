# src/ingestion/embedding.py
import json
import pickle
from pathlib import Path
import numpy as np
from tqdm import tqdm
from src.ingestion.embedder import Embedder

# running command: 
# ➜ /workspaces/enterprise-knowledge-copilot (main) $ /workspaces/enterprise-knowledge-copilot/.venv/bin/python -m src.ingestion.embedding

SRC_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SRC_DIR.parent.parent

# Resolve absolute paths for input data, model, and output
INPUT_CHUNKED_JSON = PROJECT_ROOT / "data/processed/chunked_documents.json"
OUTPUT_EMBEDDINGS_NPY = PROJECT_ROOT / "data/embeddings/embeddings.npy"
OUTPUT_METADATA_PKL = PROJECT_ROOT / "data/embeddings/embedding_metadata.pkl"
MODEL_PATH = SRC_DIR / "models" / "Xenova" / "all-MiniLM-L6-v2"

# Instantiate embedder
embedder = Embedder(path=MODEL_PATH)


def generate_onnx_embeddings():
    if not INPUT_CHUNKED_JSON.exists():
        print(f"Error: {INPUT_CHUNKED_JSON} not found. Run chunker.py first.")
        return

    with open(INPUT_CHUNKED_JSON, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    print(f"Loaded {len(chunks)} chunks to embed.")

    # 1. Format text with title metadata for higher RAG context precision
    texts_to_embed = [
        f"Title: {c.get('title', '')}\nContent: {c.get('text', '')}"
        for c in chunks
    ]

    # 2. Batch Ingestion
    batch_size = 32
    all_vectors = []

    print("Generating ONNX embeddings...")
    for i in tqdm(range(0, len(texts_to_embed), batch_size)):
        batch_texts = texts_to_embed[i : i + batch_size]
        batch_vectors = embedder.encode_batch(batch_texts)
        all_vectors.append(batch_vectors)

    embeddings_matrix = np.vstack(all_vectors).astype(np.float32)

    # 3. Save numpy embeddings array
    OUTPUT_EMBEDDINGS_NPY.parent.mkdir(parents=True, exist_ok=True)
    np.save(OUTPUT_EMBEDDINGS_NPY, embeddings_matrix)
    print(
        f"Saved matrix: {OUTPUT_EMBEDDINGS_NPY} (Shape: {embeddings_matrix.shape})"
    )

    # 4. Save index-aligned metadata
    metadata = []
    for idx, c in enumerate(chunks):
        metadata.append({
            "vector_index": idx,
            "chunk_id": c.get("chunk_id"),
            "document_id": c.get("document_id"),
            "title": c.get("title"),
            "category": c.get("category"),
            "source": c.get("source"),
            "text": c.get("text"),
        })

    with open(OUTPUT_METADATA_PKL, "wb") as f:
        pickle.dump(metadata, f)

    print(f"Saved metadata list: {OUTPUT_METADATA_PKL}")


if __name__ == "__main__":
    generate_onnx_embeddings()