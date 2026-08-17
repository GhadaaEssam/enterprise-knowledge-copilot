"""src/eval/generate_answers.py

Step 1 of the eval pipeline: runs KnowledgeAgent.ask() over the sampled
ground-truth questions and saves the full trajectory (answer, tool calls,
messages) alongside each item's ground truth fields.

Deliberately separate from judging (src/eval/run_eval.py) so that:
  - you can inspect/sanity-check raw agent answers before spending judge
    API calls on them
  - a judge-side bug or prompt tweak doesn't require re-running the agent
    (and re-burning API calls) to fix

CHECKPOINTED: writes results incrementally to --out after every question,
and on restart skips any _sample_id already present in --out. If you hit a
rate limit or the process dies at question 63/100, re-running the same
command picks up at 63 instead of starting over.

Usage:
    python -m src.evaluation.generate_answers --sample data/gt/ground_truth_sample.json --out data/gt/generations.json
"""

import argparse
import json
import logging
import time
from pathlib import Path
from typing import Any

from src.agent.agent import KnowledgeAgent

logger = logging.getLogger(__name__)


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: Any) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    tmp.replace(path)


def generate_answers(
    agent: KnowledgeAgent,
    sample: list[dict[str, Any]],
    out_path: Path,
    max_retries: int = 3,
    retry_backoff_seconds: float = 5.0,
    delay_between_questions_seconds: float = 2.0,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = load_json(out_path) if out_path.exists() else []
    done_ids = {r["_sample_id"] for r in results}

    if done_ids:
        print(f"Resuming: {len(done_ids)}/{len(sample)} already generated in {out_path}")

    for item in sample:
        sample_id = item["_sample_id"]
        if sample_id in done_ids:
            continue

        question = item["question"]
        print(f"[{sample_id + 1}/{len(sample)}] {question[:80]}")

        trajectory = None
        last_error = None
        for attempt in range(1, max_retries + 1):
            try:
                trajectory = agent.ask(question, clear_history=True)
                break
            except Exception as e:
                last_error = e
                logger.warning(
                    "Generation failed for _sample_id=%s attempt %d/%d: %s",
                    sample_id, attempt, max_retries, e,
                )
                if attempt < max_retries:
                    time.sleep(retry_backoff_seconds * attempt)  # simple linear backoff

        if trajectory is None:
            trajectory = {
                "answer": None,
                "messages": [],
                "tool_calls": [],
                "iterations": 0,
                "stop_reason": f"generation_failed: {last_error}",
            }

        result = {
            "_sample_id": sample_id,
            "question": question,
            "target_chunk_id": item.get("target_chunk_id"),
            "target_document_id": item.get("target_document_id"),
            "expected_output": item.get("expected_output"),
            "agent_answer": trajectory["answer"],
            "tool_calls": trajectory["tool_calls"],
            "iterations": trajectory["iterations"],
            "stop_reason": trajectory["stop_reason"],
        }
        results.append(result)

        save_json(out_path, results)

        if delay_between_questions_seconds > 0:
            time.sleep(delay_between_questions_seconds)

    n_failed = sum(1 for r in results if r["stop_reason"] and "generation_failed" in str(r["stop_reason"]))
    print(f"\nDone: {len(results)}/{len(sample)} generated, {n_failed} failed after retries.")
    return results


def main():
    parser = argparse.ArgumentParser(description="Generate agent answers for sampled ground truth.")
    parser.add_argument("--sample", required=True, help="Path to sampled ground truth (from sample_ground_truth.py)")
    parser.add_argument("--out", required=True, help="Path to write generations (also used to resume).")
    parser.add_argument(
        "--delay",
        type=float,
        default=2.0,
        help="Seconds to pause between questions, to avoid bursting Groq's rate limit (default: 2.0).",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    # --- Adjust to your actual wiring (matches src/tools/tool_registry.py) ---
    from src.tools.tool_registry import ToolRegistry, INTERNAL_SEARCH_SCHEMA, WEB_SEARCH_SCHEMA
    from src.tools.handlers import search_internal_documentation, search_web
    from groq import Groq
    from dotenv import load_dotenv
    load_dotenv()
    import os

    groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    tool_registry = ToolRegistry()
    tool_registry.register(INTERNAL_SEARCH_SCHEMA, search_internal_documentation)
    tool_registry.register(WEB_SEARCH_SCHEMA, search_web)
    agent = KnowledgeAgent(tool_registry=tool_registry, llm_client=groq_client)
    # ---------------------------------------------------------------------

    sample = load_json(args.sample)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    generate_answers(agent, sample, out_path, delay_between_questions_seconds=args.delay)


if __name__ == "__main__":
    main()