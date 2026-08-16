"""End-to-end, file-backed ingestion pipeline."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path

from src.ingestion.chunker import chunk_documents
from src.ingestion.cleaner import build_metadata_from_path, clean_rag_text
from src.ingestion.embedding import generate_onnx_embeddings
from src.ingestion.scraper import DEFAULT_START_URL, scrape_site


@dataclass(frozen=True)
class IngestionResult:
    raw_documents: int
    cleaned_documents: int
    chunks: int
    embeddings: int
    cleaned_documents_path: Path
    chunks_path: Path
    embeddings_path: Path
    metadata_path: Path


class IngestionPipeline:
    """Scrape, clean, chunk, and embed one documentation collection.

    Persistent artifacts are kept under ``data/processed/<collection>`` and
    ``data/embeddings/<collection>``. Raw pages and individual cleaned Markdown
    files are temporary and are removed at the end when ``cleanup=True``.
    """

    def __init__(
        self,
        start_url: str = DEFAULT_START_URL,
        *,
        collection: str = "hmn_engineering_docs",
        project_root: str | Path | None = None,
        model_path: str | Path | None = None,
        batch_size: int = 32,
    ) -> None:
        if collection in {".", ".."} or not collection or Path(collection).name != collection:
            raise ValueError("collection must be a single directory name")
        if batch_size < 1:
            raise ValueError("batch_size must be greater than zero")
        self.start_url = start_url
        self.batch_size = batch_size
        self.project_root = Path(project_root or Path(__file__).resolve().parents[2]).resolve()
        self.raw_dir = self.project_root / "data" / "raw" / collection
        self.processed_dir = self.project_root / "data" / "processed" / collection
        self.embeddings_dir = self.project_root / "data" / "embeddings" / collection
        self.cleaned_documents_path = self.processed_dir / "cleaned_documents.json"
        self.chunks_path = self.processed_dir / "chunked_documents.json"
        self.embeddings_path = self.embeddings_dir / "embeddings.npy"
        self.metadata_path = self.embeddings_dir / "embedding_metadata.pkl"
        self.model_path = Path(model_path or Path(__file__).parent / "models" / "Xenova" / "all-MiniLM-L6-v2")

    def run(self, *, cleanup: bool = True) -> IngestionResult:
        """Run all stages and return paths/counts for the persisted artifacts."""
        self._reset_directory(self.raw_dir)
        raw_files = scrape_site(self.start_url, self.raw_dir)
        if not raw_files:
            raise RuntimeError("Scraping produced no documents; no artifacts were generated")

        documents = self._clean(raw_files)
        chunks = chunk_documents(documents)
        self._write_json(self.chunks_path, chunks)
        embeddings = self._embed(chunks)

        if cleanup:
            self.cleanup_intermediate_files()

        return IngestionResult(
            raw_documents=len(raw_files), cleaned_documents=len(documents), chunks=len(chunks),
            embeddings=len(embeddings), cleaned_documents_path=self.cleaned_documents_path,
            chunks_path=self.chunks_path, embeddings_path=self.embeddings_path,
            metadata_path=self.metadata_path,
        )

    def cleanup_intermediate_files(self) -> None:
        """Remove only this pipeline's raw and per-document cleaned artifacts."""
        self._remove_directory(self.raw_dir)
        self._remove_directory(self.processed_dir / "documents")

    def _clean(self, raw_files: list[Path]) -> list[dict]:
        documents: list[dict] = []
        clean_dir = self.processed_dir / "documents"
        self._reset_directory(clean_dir)
        for raw_file in raw_files:
            cleaned = clean_rag_text(raw_file.read_text(encoding="utf-8"))
            if not cleaned:
                continue
            document = build_metadata_from_path(raw_file)
            document["text"] = cleaned
            documents.append(document)
            (clean_dir / raw_file.name).write_text(cleaned, encoding="utf-8")
        self._write_json(self.cleaned_documents_path, documents)
        return documents

    def _embed(self, chunks: list[dict]):
        if not chunks:
            raise RuntimeError("Chunking produced no chunks; embeddings were not generated")
        return generate_onnx_embeddings(
            chunks,
            embeddings_path=self.embeddings_path,
            metadata_path=self.metadata_path,
            model_path=self.model_path,
            batch_size=self.batch_size,
        )

    @staticmethod
    def _write_json(path: Path, value: object) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")

    @staticmethod
    def _reset_directory(path: Path) -> None:
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _remove_directory(path: Path) -> None:
        if path.exists():
            shutil.rmtree(path)


if __name__ == "__main__":
    result = IngestionPipeline().run()
    print(f"Ingested {result.cleaned_documents} documents into {result.chunks} chunks.")