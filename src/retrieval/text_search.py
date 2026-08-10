# src/retrieval/keyword_search.py
import os
from typing import Any, Dict, List
from sqlitesearch import TextSearchIndex


def build_sqlitesearch_index(
    documents: List[Dict[str, Any]],
    db_path: str = "hnm.db",
    overwrite: bool = True,
) -> TextSearchIndex:

    if overwrite and os.path.exists(db_path):
        os.remove(db_path)

    # Register actual text columns into FTS
    index = TextSearchIndex(
        text_fields=["title", "text", "category", "subcategory"],
        id_field="chunk_id",
        db_path=db_path,
    )

    index.fit(documents)
    return index