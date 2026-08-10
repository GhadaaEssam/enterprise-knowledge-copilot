"""src/evaluation/retry_failed.py

Removes any generation whose stop_reason isn't "completed" from an
existing generations.json, so that re-running generate_answers.py (which
skips any _sample_id already present) will retry ONLY those failed items
instead of the full 100 -- keeps you within your API budget.

Usage:
    python -m src.evaluation.retry_failed --generations eval_data/generations.json
    # then:
    python -m src.evaluation.generate_answers \\
        --sample eval_data/ground_truth_sample.json \\
        --out eval_data/generations.json
"""

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Strip failed items from generations.json for retry.")
    parser.add_argument("--generations", required=True, help="Path to generations.json to clean up in place.")
    args = parser.parse_args()

    path = Path(args.generations)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    kept = [item for item in data if item.get("stop_reason") == "completed"]
    removed = [item for item in data if item.get("stop_reason") != "completed"]

    if not removed:
        print("Nothing to retry -- every item already has stop_reason='completed'.")
        return

    print(f"Removing {len(removed)} failed item(s), keeping {len(kept)} completed:")
    for item in removed:
        print(f"  [{item['_sample_id']}] {item['question'][:70]!r} -> {item.get('stop_reason')}")

    path.write_text(json.dumps(kept, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"\nWrote {len(kept)} items back to {path}. Re-run generate_answers.py to fill in the rest.")


if __name__ == "__main__":
    main()