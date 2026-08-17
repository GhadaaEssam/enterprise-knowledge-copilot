# src/retrieval/vector_search.py
from sqlitesearch import VectorSearchIndex
from typing import List, Dict, Any
import numpy as np
from pathlib import Path


def build_vsqlitesearch_index(
    documents: List[Dict[str, Any]], 
    vectors: np.ndarray, 
    db_path: str | Path = "data/db/hmn_engineering_docs_vector.db",
    mode: str = "ivf",
    overwrite: bool = True
) -> VectorSearchIndex:

    output_path = Path(db_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if overwrite and output_path.exists():
        output_path.unlink()
    
    vs_index = VectorSearchIndex(
        keyword_fields=["category", "subcategory", "source", "document_id"],
        mode=mode,
        db_path=str(output_path)
    )

    # Ensure vectors are float32 numpy array
    vectors_np = np.asarray(vectors, dtype=np.float32)

    vs_index.fit(vectors_np, documents)

    return vs_index
