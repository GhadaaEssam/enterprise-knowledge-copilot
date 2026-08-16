"""Build persistent keyword and vector indexes from ingestion artifacts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from src.retrieval.keyword_search import build_sqlitesearch_index
from src.retrieval.vector_search import build_vsqlitesearch_index


@dataclass(frozen=True)
class IndexBuildResult:
    documents: int
    keyword_db_path: Path
    vector_db_path: Path


class IndexBuilder:
    """Create the keyword and vector SQLite indexes used by retrieval.

    By default, input comes from ``IngestionPipeline`` output for the named
    collection and both SQLite database files are stored in ``data/db``.
    """

    def __init__(
        self,
        *,
        collection: str = "hmn_engineering_docs",
        project_root: str | Path | None = None,
        chunks_path: str | Path | None = None,
        embeddings_path: str | Path | None = None,
        db_dir: str | Path | None = None,
        vector_mode: str = "ivf",
    ) -> None:
        if collection in {"", ".", ".."} or Path(collection).name != collection:
            raise ValueError("collection must be a single directory name")
        self.project_root = Path(project_root or Path(__file__).resolve().parents[2]).resolve()
        self.chunks_path = Path(chunks_path or self.project_root / "data" / "processed" / collection / "chunked_documents.json")
        self.embeddings_path = Path(embeddings_path or self.project_root / "data" / "embeddings" / collection / "embeddings.npy")
        self.db_dir = Path(db_dir or self.project_root / "data" / "db")
        self.keyword_db_path = self.db_dir / f"{collection}_keyword.db"
        self.vector_db_path = self.db_dir / f"{collection}_vector.db"
        self.vector_mode = vector_mode

    def build(self, *, overwrite: bool = True) -> IndexBuildResult:
        """Build both indexes from the persisted chunks and embeddings."""
        documents = self._load_documents()
        vectors = self._load_vectors(expected_count=len(documents))
        self.db_dir.mkdir(parents=True, exist_ok=True)

        keyword_index = build_sqlitesearch_index(
            documents, db_path=str(self.keyword_db_path), overwrite=overwrite
        )
        self._close(keyword_index)
        vector_index = build_vsqlitesearch_index(
            documents,
            vectors,
            db_path=str(self.vector_db_path),
            mode=self.vector_mode,
            overwrite=overwrite,
        )
        self._close(vector_index)
        return IndexBuildResult(
            documents=len(documents),
            keyword_db_path=self.keyword_db_path,
            vector_db_path=self.vector_db_path,
        )

    def _load_documents(self) -> list[dict[str, Any]]:
        if not self.chunks_path.exists():
            raise FileNotFoundError(f"Chunk file not found: {self.chunks_path}")
        with self.chunks_path.open(encoding="utf-8") as file:
            documents = json.load(file)
        if not isinstance(documents, list) or not documents:
            raise ValueError("Chunk file must contain a non-empty JSON list")
        return documents

    def _load_vectors(self, *, expected_count: int) -> np.ndarray:
        if not self.embeddings_path.exists():
            raise FileNotFoundError(f"Embeddings file not found: {self.embeddings_path}")
        vectors = np.load(self.embeddings_path)
        if vectors.ndim != 2 or len(vectors) != expected_count:
            raise ValueError(
                f"Expected {expected_count} embedding vectors, found shape {vectors.shape}"
            )
        return np.asarray(vectors, dtype=np.float32)

    @staticmethod
    def _close(index: object) -> None:
        close = getattr(index, "close", None)
        if callable(close):
            close()


if __name__ == "__main__":
    result = IndexBuilder().build()
    print(f"Built indexes for {result.documents} chunks in {result.keyword_db_path.parent}")