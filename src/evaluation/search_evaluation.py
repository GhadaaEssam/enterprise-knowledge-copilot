import json
import pandas as pd
from typing import Dict, List, Any
from tqdm import tqdm



def evaluate_engine(
    engine, ground_truth: List[Dict[str, Any]], num_results: int = 5
) -> Dict[str, float]:
    """Evaluates a search engine instance against ground truth queries for Hit Rate and MRR."""
    hits = 0
    reciprocal_ranks = []

    for item in tqdm(ground_truth, desc=f"Evaluating {engine.__class__.__name__}"):
        query = item.get("question")
        target_id = item.get("target_chunk_id") 

        if not query or not target_id:
            continue

        # Execute search
        results = engine.search(query=query, num_results=num_results)

        # Extract IDs from retrieved search results
        retrieved_ids = [
            doc.get("chunk_id") for doc in results
        ]

        # Calculate Hit and Reciprocal Rank
        if target_id in retrieved_ids:
            hits += 1
            rank = retrieved_ids.index(target_id) + 1  # 1-based rank
            reciprocal_ranks.append(1.0 / rank)
        else:
            reciprocal_ranks.append(0.0)

    total_queries = len(ground_truth)
    hit_rate = hits / total_queries if total_queries > 0 else 0.0
    mrr = (
        sum(reciprocal_ranks) / total_queries
        if total_queries > 0
        else 0.0
    )

    return {
        "Engine": engine.__class__.__name__,
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