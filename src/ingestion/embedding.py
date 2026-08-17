"""Embedding artifact generation for chunked ingestion documents."""

from __future__ import annotations

import json
import pickle
from pathlib import Path

import numpy as np

from src.ingestion.embedder import Embedder


SRC_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SRC_DIR.parent.parent
DEFAULT_COLLECTION = "hmn_engineering_docs"
INPUT_CHUNKED_JSON = PROJECT_ROOT / "data" / "processed" / DEFAULT_COLLECTION / "chunked_documents.json"
OUTPUT_EMBEDDINGS_NPY = PROJECT_ROOT / "data" / "embeddings" / DEFAULT_COLLECTION / "embeddings.npy"
OUTPUT_METADATA_PKL = PROJECT_ROOT / "data" / "embeddings" / DEFAULT_COLLECTION / "embedding_metadata.pkl"
MODEL_PATH = SRC_DIR / "embed" / "models" / "Xenova" / "all-MiniLM-L6-v2"


def generate_onnx_embeddings(
    chunks: list[dict],
    *,
    embeddings_path: str | Path,
    metadata_path: str | Path,
    model_path: str | Path = MODEL_PATH,
    batch_size: int = 32,
) -> np.ndarray:
    """Embed chunks and persist index-aligned vectors and metadata."""
    if not chunks:
        raise ValueError("Cannot generate embeddings for an empty chunk list")
    if batch_size < 1:
        raise ValueError("batch_size must be greater than zero")

    embedder = Embedder(model_path)
    texts = [f"Title: {chunk.get('title', '')}\nContent: {chunk.get('text', '')}" for chunk in chunks]
    batches = [
        embedder.encode_batch(texts[index:index + batch_size])
        for index in range(0, len(texts), batch_size)
    ]
    matrix = np.vstack(batches).astype(np.float32)

    output_vectors = Path(embeddings_path)
    output_metadata = Path(metadata_path)
    output_vectors.parent.mkdir(parents=True, exist_ok=True)
    output_metadata.parent.mkdir(parents=True, exist_ok=True)
    np.save(output_vectors, matrix)
    with output_metadata.open("wb") as file:
        pickle.dump([{"vector_index": index, **chunk} for index, chunk in enumerate(chunks)], file)
    return matrix


def generate_embeddings_from_file(
    input_path: str | Path = INPUT_CHUNKED_JSON,
    *,
    embeddings_path: str | Path = OUTPUT_EMBEDDINGS_NPY,
    metadata_path: str | Path = OUTPUT_METADATA_PKL,
    model_path: str | Path = MODEL_PATH,
    batch_size: int = 32,
) -> np.ndarray:
    """Backward-compatible file-based entry point for standalone embedding."""
    with Path(input_path).open(encoding="utf-8") as file:
        return generate_onnx_embeddings(
            json.load(file), embeddings_path=embeddings_path, metadata_path=metadata_path,
            model_path=model_path, batch_size=batch_size,
        )


if __name__ == "__main__":
    matrix = generate_embeddings_from_file()
    print(f"Saved {len(matrix)} embeddings to {OUTPUT_EMBEDDINGS_NPY}")
