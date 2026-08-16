"""Standalone retrieval evaluation for the project's search engines."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from tqdm import tqdm

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.retrieval.search_engines import (  # noqa: E402
    HybridSearchEngine,
    KeywordSearchEngine,
    SqliteVectorSearchEngine,
)

DEFAULT_COLLECTION = "hmn_engineering_docs"
DEFAULT_GROUND_TRUTH_PATH = PROJECT_ROOT / "data" / "ground_truth.json"
DEFAULT_DB_DIR = PROJECT_ROOT / "data" / "db"
DEFAULT_MODEL_PATH = (
    PROJECT_ROOT
    / "src"
    / "ingestion"
    / "embed"
    / "models"
    / "Xenova"
    / "all-MiniLM-L6-v2"
)

# run command: uv run python -m src.evaluation.search_evaluation --output data\results\retrieval_metrics.csv


def _result_id(result: Dict[str, Any]) -> Optional[str]:
    """Return the stable chunk identifier used across retrieval engines."""
    result_id = result.get("chunk_id") or result.get("id")
    return str(result_id) if result_id is not None else None


def evaluate_engine(
    engine, ground_truth: List[Dict[str, Any]], num_results: int = 5
) -> Dict[str, float]:
    """Evaluates a search engine instance against ground truth queries for Hit Rate and MRR."""
    hits = 0
    reciprocal_ranks = []

    evaluated_queries = 0

    for item in tqdm(ground_truth, desc=f"Evaluating {engine.__class__.__name__}"):
        query = item.get("question")
        target_id = item.get("target_chunk_id")

        if not query or not target_id:
            continue

        evaluated_queries += 1
        target_id = str(target_id)

        # Execute search
        results = engine.search(query=query, num_results=num_results)

        # Extract IDs from retrieved search results
        retrieved_ids = [_result_id(doc) for doc in results]

        # Calculate Hit and Reciprocal Rank
        if target_id in retrieved_ids:
            hits += 1
            rank = retrieved_ids.index(target_id) + 1  # 1-based rank
            reciprocal_ranks.append(1.0 / rank)
        else:
            reciprocal_ranks.append(0.0)

    hit_rate = hits / evaluated_queries if evaluated_queries > 0 else 0.0
    mrr = (
        sum(reciprocal_ranks) / evaluated_queries
        if evaluated_queries > 0
        else 0.0
    )

    return {
        "Engine": engine.__class__.__name__,
        "Queries": evaluated_queries,
        f"Hit Rate@{num_results}": round(hit_rate, 4),
        f"MRR@{num_results}": round(mrr, 4),
    }


def run_evaluation(
    keyword_engine, sqlite_vector_engine, hybrid_engine, ground_truth_path: str, num_results: int = 5
) -> pd.DataFrame:
    # 1. Load ground truth JSON
    with open(ground_truth_path, "r", encoding="utf-8") as f:
        ground_truth = json.load(f)

    engines = [keyword_engine, sqlite_vector_engine, hybrid_engine]
    eval_metrics = []

    # 2. Evaluate each engine
    for engine in engines:
        metrics = evaluate_engine(
            engine, ground_truth, num_results=num_results
        )
        eval_metrics.append(metrics)

    # 3. Format into comparative Summary Table
    df = pd.DataFrame(eval_metrics)
    return df


def build_engines(
    *,
    keyword_db_path: str | Path,
    vector_db_path: str | Path,
    model_path: str | Path,
    hybrid_k: int = 60,
    keyword_weight: float = 1.5,
    vector_weight: float = 1.0,
) -> list:
    """Create the three retrieval engines evaluated by this script."""
    keyword_engine = KeywordSearchEngine.from_db(str(keyword_db_path))
    vector_engine = SqliteVectorSearchEngine.from_db(
        str(vector_db_path),
        str(model_path),
    )
    hybrid_engine = HybridSearchEngine(
        keyword_engine=keyword_engine,
        vector_engine=vector_engine,
        k=hybrid_k,
        keyword_weight=keyword_weight,
        vector_weight=vector_weight,
    )
    return [keyword_engine, vector_engine, hybrid_engine]


def validate_paths(
    *,
    ground_truth_path: Path,
    keyword_db_path: Path,
    vector_db_path: Path,
    model_path: Path,
) -> None:
    required_files = {
        "ground truth": ground_truth_path,
        "keyword index": keyword_db_path,
        "vector index": vector_db_path,
        "ONNX model": model_path / "model.onnx",
        "tokenizer": model_path / "tokenizer.json",
    }
    missing = [f"{label}: {path}" for label, path in required_files.items() if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "Missing required evaluation artifact(s):\n"
            + "\n".join(f"- {item}" for item in missing)
        )


def load_ground_truth(path: str | Path) -> list[dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError("Ground truth file must contain a JSON list")
    return data


def evaluate_search_engines(
    *,
    ground_truth_path: str | Path = DEFAULT_GROUND_TRUTH_PATH,
    keyword_db_path: str | Path | None = None,
    vector_db_path: str | Path | None = None,
    model_path: str | Path = DEFAULT_MODEL_PATH,
    collection: str = DEFAULT_COLLECTION,
    num_results: int = 5,
    hybrid_k: int = 60,
    keyword_weight: float = 1.5,
    vector_weight: float = 1.0,
) -> pd.DataFrame:
    """Load artifacts, instantiate all retrieval engines, and return metrics."""
    keyword_db_path = Path(keyword_db_path or DEFAULT_DB_DIR / f"{collection}_keyword.db")
    vector_db_path = Path(vector_db_path or DEFAULT_DB_DIR / f"{collection}_vector.db")
    ground_truth_path = Path(ground_truth_path)
    model_path = Path(model_path)

    validate_paths(
        ground_truth_path=ground_truth_path,
        keyword_db_path=keyword_db_path,
        vector_db_path=vector_db_path,
        model_path=model_path,
    )

    ground_truth = load_ground_truth(ground_truth_path)
    engines = build_engines(
        keyword_db_path=keyword_db_path,
        vector_db_path=vector_db_path,
        model_path=model_path,
        hybrid_k=hybrid_k,
        keyword_weight=keyword_weight,
        vector_weight=vector_weight,
    )
    return pd.DataFrame(
        [evaluate_engine(engine, ground_truth, num_results=num_results) for engine in engines]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate Keyword, SQLite vector, and Hybrid retrieval engines."
    )
    parser.add_argument("--ground-truth", type=Path, default=DEFAULT_GROUND_TRUTH_PATH)
    parser.add_argument("--collection", default=DEFAULT_COLLECTION)
    parser.add_argument("--keyword-db", type=Path)
    parser.add_argument("--vector-db", type=Path)
    parser.add_argument("--model-path", type=Path, default=DEFAULT_MODEL_PATH)
    parser.add_argument("--num-results", type=int, default=5)
    parser.add_argument("--hybrid-k", type=int, default=60)
    parser.add_argument("--keyword-weight", type=float, default=1.5)
    parser.add_argument("--vector-weight", type=float, default=1.0)
    parser.add_argument("--output", type=Path, help="Optional CSV path for metrics.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = evaluate_search_engines(
        ground_truth_path=args.ground_truth,
        keyword_db_path=args.keyword_db,
        vector_db_path=args.vector_db,
        model_path=args.model_path,
        collection=args.collection,
        num_results=args.num_results,
        hybrid_k=args.hybrid_k,
        keyword_weight=args.keyword_weight,
        vector_weight=args.vector_weight,
    )

    print(results.to_string(index=False))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        results.to_csv(args.output, index=False)
        print(f"\nSaved evaluation metrics to {args.output}")


if __name__ == "__main__":
    main()