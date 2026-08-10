import itertools
from typing import Any, Dict, List, Tuple


def calculate_metrics(
    eval_dataset: List[Dict[str, Any]],
    engine: Any,
    boost_dict: Dict[str, float] = None,
    num_results: int = 5,
) -> Tuple[float, float]:
    """Calculates Hit Rate@5 and MRR@5 across an evaluation dataset.

    eval_dataset expects entries with:
      - 'question': the test search query string
      - 'chunk_id': expected relevant chunk ID
    """
    hits = 0
    reciprocal_ranks = []

    for item in eval_dataset:
        query = item["question"]
        expected_id = item.get("target_chunk_id")

        # Execute search pass
        search_kwargs = {"num_results": num_results}
        if boost_dict is not None:
            search_kwargs["boost_dict"] = boost_dict

        results = engine.search(query, **search_kwargs)

        # Retrieve list of returned IDs
        returned_ids = [
            doc.get("chunk_id") for doc in results
        ]

        # Calculate Hit Rate & Reciprocal Rank
        if expected_id in returned_ids:
            hits += 1
            rank = returned_ids.index(expected_id) + 1
            reciprocal_ranks.append(1.0 / rank)
        else:
            reciprocal_ranks.append(0.0)

    hit_rate = hits / len(eval_dataset) if eval_dataset else 0.0
    mrr = (
        sum(reciprocal_ranks) / len(reciprocal_ranks)
        if reciprocal_ranks
        else 0.0
    )

    return hit_rate, mrr

def evaluate_keyword_boosts(eval_dataset, keyword_engine):
    best_mrr = 0.0
    best_boosts = None

    # Test distinct weight ratios for title and category against text (1.0 baseline)
    title_weights = [1.0, 2.0, 3.0, 5.0]
    category_weights = [0.5, 1.0, 2.0]

    for t_w, c_w in itertools.product(title_weights, category_weights):
        trial_boosts = {
            "title": t_w,
            "category": c_w,
            "subcategory": c_w,
            "text": 1.0,  # Fixed baseline
        }

        hit_rate, mrr = calculate_metrics(
            eval_dataset, keyword_engine, boost_dict=trial_boosts
        )

        print(
            f"Boosts: {trial_boosts} -> Hit Rate@5: {hit_rate:.4f}, MRR@5: {mrr:.5f}"
        )

        if mrr > best_mrr:
            best_mrr = mrr
            best_boosts = trial_boosts

    print("\n--- Optimal Field Boosts ---")
    print(f"Best Weights: {best_boosts}")
    print(f"Best MRR@5: {best_mrr:.5f}")

    return best_boosts