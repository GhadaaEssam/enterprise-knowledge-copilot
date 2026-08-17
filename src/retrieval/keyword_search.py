# src/retrieval/keyword_search.py
from pathlib import Path
from typing import Any, Dict, List
from sqlitesearch import TextSearchIndex


def build_sqlitesearch_index(
    documents: List[Dict[str, Any]],
    db_path: str | Path = "data/db/hmn_engineering_docs_keyword.db",
    overwrite: bool = True,
) -> TextSearchIndex:

    output_path = Path(db_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if overwrite and output_path.exists():
        output_path.unlink()

    # Register actual text columns into FTS
    index = TextSearchIndex(
        text_fields=["title", "text", "category", "subcategory"],
        id_field="chunk_id",
        db_path=str(output_path),
    )

    index.fit(documents)
    return index
