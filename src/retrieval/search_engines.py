import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import minsearch
import numpy as np
from sqlitesearch import TextSearchIndex, VectorSearchIndex

PROJECT_ROOT = Path.cwd().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.ingestion.embedder import Embedder


class BaseSearchEngine:

    def search(
        self, query: str, num_results: int = 5, **kwargs
    ) -> List[Dict[str, Any]]:
        raise NotImplementedError


class KeywordSearchEngine(BaseSearchEngine):

    def __init__(
        self,
        sqlitesearch_index: TextSearchIndex,
    ):
        self.index = sqlitesearch_index

    @classmethod
    def from_db(
        cls,
        db_path: str,
        text_fields: Optional[List[str]] = None,
        keyword_fields: Optional[List[str]] = None,
    ):
        index = TextSearchIndex(
            text_fields=text_fields
            or ["title", "text", "category", "subcategory"],
            keyword_fields=keyword_fields or ["category", "subcategory"],
            db_path=db_path,
        )
        return cls(sqlitesearch_index=index)

    def search(
        self,
        query: str,
        num_results: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> List[Dict[str, Any]]:

        results = self.index.search(
            query=query,
            num_results=num_results,
            filter_dict=filter_dict,
        )
        return results


class SqliteVectorSearchEngine(BaseSearchEngine):

    def __init__(self, embedder, index: VectorSearchIndex):
        self.embedder = embedder
        self.index = index

    @classmethod
    def from_db(
        cls, 
        db_path: str, 
        model_path: str, 
        mode: str = "ivf",
        keyword_fields: Optional[List[str]] = None
    ):
        """Loads an existing vector search index from a SQLite .db file without re-embedding."""
        embedder = Embedder(path=model_path)
        index = VectorSearchIndex(
            db_path=db_path,
            mode=mode,
            keyword_fields=keyword_fields or ["category", "subcategory", "source", "document_id"]
        )
        return cls(embedder=embedder, index=index)

    def search(
        self,
        query: str,
        num_results: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        query_vector = self.embedder.encode(query)
        if isinstance(query_vector, list):
            query_vector = np.array(query_vector, dtype=np.float32)

        results = self.index.search(
            query_vector=query_vector,
            num_results=num_results,
            filter_dict=filter_dict,
        )
        return results


class HybridSearchEngine(BaseSearchEngine):

    def __init__(
        self,
        keyword_engine: BaseSearchEngine,
        vector_engine: BaseSearchEngine,
        k: int = 60,
        keyword_weight: float = 1.5,  # Give Keyword engine higher authority
        vector_weight: float = 1.0,
    ):
        self.keyword_engine = keyword_engine
        self.vector_engine = vector_engine
        self.k = k
        self.keyword_weight = keyword_weight
        self.vector_weight = vector_weight

    @classmethod
    def from_db(
        cls,
        keyword_db_path: str,
        vector_db_path: str,
        model_path: str,
        k: int = 60,
        keyword_weight: float = 1.5,
        vector_weight: float = 1.0,
    ):
        keyword_engine = KeywordSearchEngine.from_db(keyword_db_path)
        vector_engine = SqliteVectorSearchEngine.from_db(
            vector_db_path, model_path
        )
        return cls(
            keyword_engine=keyword_engine,
            vector_engine=vector_engine,
            k=k,
            keyword_weight=keyword_weight,
            vector_weight=vector_weight,
        )

    def search(
        self,
        query: str,
        num_results: int = 5,
        fetch_k: int = 20,
        filter_dict: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> List[Dict[str, Any]]:

        # Pass boost_dict and filter_dict down to Keyword search
        keyword_results = self.keyword_engine.search(
            query,
            num_results=fetch_k,
            filter_dict=filter_dict,
        )

        # Pass filter_dict down to Vector search
        vector_results = self.vector_engine.search(
            query, num_results=fetch_k, filter_dict=filter_dict
        )

        rrf_scores = {}
        doc_map = {}

        # 1. Apply Weighted RRF for Keyword Search
        for rank, doc in enumerate(keyword_results):
            doc_id = doc.get("chunk_id") or doc.get("id")
            if not doc_id:
                continue
            doc_map[doc_id] = doc
            rrf_scores[doc_id] = rrf_scores.get(
                doc_id, 0.0
            ) + self.keyword_weight / (self.k + (rank + 1))

        # 2. Apply Weighted RRF for Vector Search
        for rank, doc in enumerate(vector_results):
            doc_id = doc.get("chunk_id") or doc.get("id")
            if not doc_id:
                continue
            doc_map[doc_id] = doc
            rrf_scores[doc_id] = rrf_scores.get(
                doc_id, 0.0
            ) + self.vector_weight / (self.k + (rank + 1))

        # Sort combined candidate list by Weighted RRF score
        sorted_doc_ids = sorted(
            rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True
        )

        fused_results = []
        for doc_id in sorted_doc_ids[:num_results]:
            doc = dict(doc_map[doc_id])
            doc["_rrf_score"] = rrf_scores[doc_id]
            fused_results.append(doc)

        return fused_results