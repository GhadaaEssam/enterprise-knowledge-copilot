# src/retrieval/vector_search.py
from sqlitesearch import VectorSearchIndex
from typing import List, Dict, Any
import numpy as np
import os


def build_vsqlitesearch_index(
    documents: List[Dict[str, Any]], 
    vectors: np.ndarray, 
    db_path: str = "hnm_vectors.db",
    mode: str = "ivf",
    overwrite: bool = True
) -> VectorSearchIndex:

    if overwrite and os.path.exists(db_path):
        os.remove(db_path)
    
    vs_index = VectorSearchIndex(
        keyword_fields=["category", "subcategory", "source", "document_id"],
        mode=mode,
        db_path=db_path
    )

    # Ensure vectors are float32 numpy array
    vectors_np = np.asarray(vectors, dtype=np.float32)

    vs_index.fit(vectors_np, documents)

    vs_index.close()
    print("Done. vectors saved to hnm_vectors.db")

    return vs_index