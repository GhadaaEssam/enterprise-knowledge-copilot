"""src/tools/internal_search.py"""

from typing import Any, Dict, List, Optional
from pathlib import Path
import sys

PROJECT_ROOT = Path.cwd().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.retrieval.search_engines import KeywordSearchEngine


class InternalSearchTool:

    def __init__(
        self,
        db_path: str = "data/db/hmn_engineering_docs_keyword.db",
        search_engine: Optional[KeywordSearchEngine] = None,
    ):
        # Use provided instance or instantiate directly from SQLite DB path
        if search_engine:
            self.search_engine = search_engine
        else:
            self.search_engine = KeywordSearchEngine.from_db(db_path=db_path)

    def search(
        self,
        query: str,
        num_results: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:

        return self.search_engine.search(
            query=query,
            num_results=num_results,
            filter_dict=filter_dict
        )

    def format_context(self, search_results: List[Dict[str, Any]]) -> str:
        """Formats search results into structured LLM context."""

        if not search_results:
            return "No relevant internal documentation found."

        sections = []
        for i, doc in enumerate(search_results, 1):
            chunk_id = doc.get("chunk_id", "N/A")
            document_id = doc.get("document_id", "N/A")
            title = doc.get("title", "Untitled")
            category = doc.get("category", "N/A")
            source = doc.get("source", "N/A")
            text = doc.get("text", "")

            sections.append(
                f"[{i}] chunk_id: {chunk_id} | document_id: {document_id}\n"
                f"Document: {title} (Category: {category}, Source: {source})\n\n"
                f"{text}"
            )

        return "\n\n---\n\n".join(sections)
