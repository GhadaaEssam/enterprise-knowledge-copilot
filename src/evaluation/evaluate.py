"""src/evaluation/evaluate.py

Step 3 of the evaluation pipeline:

1. sample_ground_truth.py
2. generate_answers.py
3. evaluate.py

Evaluates each generated trajectory using:

LLM-JUDGED METRICS
------------------
1. correctness:
   Compares the agent answer against the expected ground-truth answer.

2. groundedness:
   Compares the agent answer against the context actually retrieved
   by the agent.

3. context_relevance:
   Evaluates whether the retrieved context is relevant to the user's
   question.

DETERMINISTIC METRIC
--------------------
4. tool_selection_accuracy:
   All 100 evaluation questions were generated from internal
   documentation, so the expected tool is always:

       search_internal_documentation

   No LLM call is required for this metric.

The script is checkpointed and safe to resume.

Usage:
    uv run python -m src.evaluation.evaluate \
        --generations data/gt/generations.json \
        --out data/results/llm_eval_report.json \
        --judge-model llama-3.3-70b-versatile
"""

import argparse
import json
import logging
import statistics
from pathlib import Path
from typing import Any

from src.evaluation.judge import judge_trajectory

logger = logging.getLogger(__name__)


# ============================================================
# JSON helpers
# ============================================================

def load_json(path: str) -> Any:
    """Load JSON from disk."""

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def save_json(
    path: Path,
    data: Any,
) -> None:
    """Atomically save JSON to disk."""

    tmp = path.with_suffix(
        path.suffix + ".tmp"
    )

    tmp.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
            default=str,
        ),
        encoding="utf-8",
    )

    tmp.replace(path)


# ============================================================
# Evaluation
# ============================================================

def evaluate(
    llm_client,
    judge_model: str,
    generations: list[dict[str, Any]],
    out_path: Path,
) -> list[dict[str, Any]]:
    """
    Evaluate generated agent trajectories.

    Results are checkpointed after every item so the evaluation
    can safely resume after rate limits or other failures.
    """

    results: list[dict[str, Any]] = (
        load_json(str(out_path))
        if out_path.exists()
        else []
    )

    done_ids = {
        r["_sample_id"]
        for r in results
    }

    if done_ids:

        print(
            f"Resuming: {len(done_ids)}/{len(generations)} "
            f"already scored in {out_path}"
        )

    for item in generations:

        sample_id = item["_sample_id"]

        if sample_id in done_ids:
            continue

        question = item["question"]

        print(
            f"[{sample_id + 1}/{len(generations)}] "
            f"scoring: {question[:80]}"
        )

        # ----------------------------------------------------
        # Build trajectory for judge.py
        # ----------------------------------------------------

        trajectory = {
            "answer": item.get(
                "agent_answer",
                "",
            ),
            "tool_calls": item.get(
                "tool_calls",
                [],
            ),
            "iterations": item.get(
                "iterations",
                0,
            ),
            "stop_reason": item.get(
                "stop_reason",
            ),
            "expected_output": item.get(
                "expected_output",
            ),
        }

        # ----------------------------------------------------
        # Run evaluation
        #
        # judge_trajectory performs:
        # - correctness
        # - groundedness
        # - context relevance
        # - deterministic tool selection
        # ----------------------------------------------------

        judged = judge_trajectory(
            llm_client=llm_client,
            judge_model=judge_model,
            question=question,
            trajectory=trajectory,
        )

        # ----------------------------------------------------
        # Save per-item result
        # ----------------------------------------------------

        result = {
            "_sample_id": sample_id,

            "question": question,

            "agent_answer": item.get(
                "agent_answer"
            ),

            "expected_output": item.get(
                "expected_output"
            ),

            "iterations": item.get(
                "iterations"
            ),

            "stop_reason": item.get(
                "stop_reason"
            ),

            # ----------------------------------------------
            # Scores
            # ----------------------------------------------

            "scores": judged["scores"],

            # ----------------------------------------------
            # Judge reasoning
            # ----------------------------------------------

            "reasoning": judged["reasoning"],

            # ----------------------------------------------
            # Deterministic tool-selection details
            # ----------------------------------------------

            "tool_selection": judged[
                "tool_selection"
            ],
        }

        results.append(result)

        # ----------------------------------------------------
        # Checkpoint
        # ----------------------------------------------------

        save_json(
            out_path,
            results,
        )

    print(
        f"\nDone: {len(results)}/{len(generations)} evaluated."
    )

    return results


# ============================================================
# Aggregation
# ============================================================

def aggregate(
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    """Calculate aggregate evaluation metrics."""

    n = len(results)

    # --------------------------------------------------------
    # LLM-judged metrics
    # --------------------------------------------------------

    def axis_stats(
        axis: str,
    ) -> dict[str, Any]:

        values = [
            r["scores"].get(axis)
            for r in results
            if r.get("scores", {}).get(axis)
            is not None
        ]

        return {
            "mean": (
                round(
                    statistics.mean(values),
                    2,
                )
                if values
                else None
            ),
            "min": (
                min(values)
                if values
                else None
            ),
            "n_scored": len(values),
            "n_missing": n - len(values),
        }

    # --------------------------------------------------------
    # Deterministic tool-selection metrics
    # --------------------------------------------------------

    tool_results = [
        r.get(
            "tool_selection",
            {},
        )
        for r in results
    ]

    tool_accuracy_values = [
        r.get("accuracy")
        for r in tool_results
        if r.get("accuracy") is not None
    ]

    correct_tool_count = sum(
        1
        for r in tool_results
        if r.get("correct") is True
    )

    internal_search_count = sum(
        1
        for r in tool_results
        if r.get("internal_search_used") is True
    )

    web_search_count = sum(
        1
        for r in tool_results
        if r.get("web_search_used") is True
    )

    no_tool_count = sum(
        1
        for r in tool_results
        if r.get("no_tool_called") is True
    )

    unnecessary_web_count = sum(
        1
        for r in tool_results
        if r.get(
            "unnecessary_web_search"
        )
        is True
    )

    return {
        "n_cases": n,

        # LLM evaluation
        "correctness": axis_stats(
            "correctness"
        ),

        "groundedness": axis_stats(
            "groundedness"
        ),

        "context_relevance": axis_stats(
            "context_relevance"
        ),

        # Deterministic routing evaluation
        "tool_selection": {
            "accuracy": (
                round(
                    statistics.mean(
                        tool_accuracy_values
                    ),
                    3,
                )
                if tool_accuracy_values
                else None
            ),
            "correct": correct_tool_count,
            "total": n,

            "internal_search_usage_rate": (
                round(
                    internal_search_count / n,
                    3,
                )
                if n
                else None
            ),

            "web_search_usage_rate": (
                round(
                    web_search_count / n,
                    3,
                )
                if n
                else None
            ),

            "no_tool_called_rate": (
                round(
                    no_tool_count / n,
                    3,
                )
                if n
                else None
            ),

            "unnecessary_web_search_rate": (
                round(
                    unnecessary_web_count / n,
                    3,
                )
                if n
                else None
            ),
        },
    }


# ============================================================
# CLI
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Evaluate generated agent answers using "
            "LLM-as-a-judge and deterministic tool selection."
        )
    )

    parser.add_argument(
        "--generations",
        required=True,
        help=(
            "Path to generations.json generated "
            "by generate_answers.py"
        ),
    )

    parser.add_argument(
        "--out",
        required=True,
        help=(
            "Path to write per-item evaluation results. "
            "Also used to resume."
        ),
    )

    parser.add_argument(
        "--judge-model",
        default="llama-3.3-70b-versatile",
        help=(
            "Model used for LLM judging. "
            "Prefer a stronger/different model from the agent."
        ),
    )

    args = parser.parse_args()

    # --------------------------------------------------------
    # LLM client
    # --------------------------------------------------------

    from dotenv import load_dotenv
    from groq import Groq

    import os

    load_dotenv()

    api_key = os.environ.get(
        "GROQ_API_KEY"
    )

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set."
        )

    groq_client = Groq(api_key=api_key)

    # --------------------------------------------------------
    # Load generations
    # --------------------------------------------------------

    generations = load_json(
        args.generations
    )

    out_path = Path(
        args.out
    )

    out_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Evaluate
    # --------------------------------------------------------

    results = evaluate(
        llm_client=groq_client,
        judge_model=args.judge_model,
        generations=generations,
        out_path=out_path,
    )

    # --------------------------------------------------------
    # Aggregate
    # --------------------------------------------------------

    summary = aggregate(
        results
    )

    print("\n=== Summary ===")

    print(
        json.dumps(
            summary,
            indent=2,
        )
    )

    print(
        f"\nPer-item scores written to {out_path}"
    )


if __name__ == "__main__":
    main()