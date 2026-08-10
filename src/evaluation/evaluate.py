"""src/evaluation/evaluate.py

Step 3 of the pipeline (after sample_ground_truth.py and generate_answers.py):
scores each generated trajectory against its ground truth.

LLM-JUDGED METRICS:

1. correctness:
   Compares agent_answer against the expected_output (ground truth).

2. groundedness:
   Compares agent_answer against what was actually retrieved by the agent,
   catching hallucinations independently of whether the answer happens to
   match the expected output.

CHECKPOINTED the same way as generate_answers.py -- safe to re-run if it
dies partway through the judge calls.

Usage:
python -m src.evaluation.evaluate \
    --generations eval_data/generations.json \
    --out eval_data/eval_report.json \
    --judge-model llama-3.3-70b-versatile
"""

import argparse
import json
import logging
import statistics
from pathlib import Path
from typing import Any

from src.evaluation.judge import judge_correctness, judge_groundedness

logger = logging.getLogger(__name__)


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: Any) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    tmp.replace(path)


def evaluate(
    llm_client,
    judge_model: str,
    generations: list[dict[str, Any]],
    out_path: Path,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = (
        load_json(str(out_path)) if out_path.exists() else []
    )

    done_ids = {r["_sample_id"] for r in results}

    if done_ids:
        print(
            f"Resuming: {len(done_ids)}/{len(generations)} "
            f"already scored in {out_path}"
        )

    for item in generations:
        sample_id = item["_sample_id"]

        if sample_id in done_ids:
            continue

        print(
            f"[{sample_id + 1}/{len(generations)}] "
            f"scoring: {item['question'][:80]}"
        )

        # LLM-based correctness evaluation
        correctness = judge_correctness(
            llm_client,
            judge_model,
            item["question"],
            item["expected_output"],
            item["agent_answer"],
        )

        # LLM-based groundedness evaluation
        groundedness = judge_groundedness(
            llm_client,
            judge_model,
            item["agent_answer"],
            item["tool_calls"],
        )

        result = {
            "_sample_id": sample_id,
            "question": item["question"],
            "agent_answer": item["agent_answer"],
            "expected_output": item.get("expected_output"),
            "scores": {
                "correctness": correctness.score,
                "groundedness": groundedness.score,
            },
            "reasoning": {
                "correctness": correctness.reasoning,
                "groundedness": groundedness.reasoning,
            },
        }

        results.append(result)

        # Checkpoint after every item
        save_json(out_path, results)

    return results

def aggregate(results: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(results)

    def axis_stats(axis: str) -> dict[str, Any]:
        values = [
            r["scores"][axis]
            for r in results
            if r["scores"][axis] is not None
        ]

        return {
            "mean": round(statistics.mean(values), 2) if values else None,
            "min": min(values) if values else None,
            "n_scored": len(values),
            "n_missing": n - len(values),
        }

    return {
        "n_cases": n,
        "correctness": axis_stats("correctness"),
        "groundedness": axis_stats("groundedness"),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate generated agent answers against ground truth."
    )

    parser.add_argument(
        "--generations",
        required=True,
        help="Path to generations.json from generate_answers.py",
    )

    parser.add_argument(
        "--out",
        required=True,
        help="Path to write per-item scores (also used to resume).",
    )

    parser.add_argument(
        "--judge-model",
        default="llama-3.3-70b-versatile",
        help=(
            "Model used for judging. Prefer something stronger than / "
            "different from the agent's own model."
        ),
    )

    args = parser.parse_args()

    from groq import Groq
    from dotenv import load_dotenv
    import os

    load_dotenv()

    groq_client = Groq(
        api_key=os.environ.get("GROQ_API_KEY")
    )

    generations = load_json(args.generations)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    results = evaluate(
        groq_client,
        args.judge_model,
        generations,
        out_path,
    )

    summary = aggregate(results)

    print("\n=== Summary ===")
    print(json.dumps(summary, indent=2))

    print(f"\nPer-item scores written to {out_path}")


if __name__ == "__main__":
    main()