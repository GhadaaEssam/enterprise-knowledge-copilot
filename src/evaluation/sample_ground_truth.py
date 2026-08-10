"""src/eval/sample_ground_truth.py

Draws a reproducible random sample from the full ground-truth set so you're
not burning API calls on all ~1100 questions. Re-running with the same
--seed always yields the same sample, so your generation/eval results stay
comparable across runs.

Usage:
    python -m src.eval.sample_ground_truth \\
        --ground-truth data/evaluation/ground_truth_augmented.json \\
        --sample-size 100 \\
        --seed 42 \\
        --out eval_data/ground_truth_sample.json
"""

import argparse
import json
import random
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Sample N items from the ground truth set.")
    parser.add_argument("--ground-truth", required=True, help="Path to full ground_truth_augmented.json")
    parser.add_argument("--sample-size", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42, help="Fixed seed for reproducible sampling.")
    parser.add_argument("--out", required=True, help="Path to write the sampled subset.")
    parser.add_argument(
        "--one-per-chunk",
        action="store_true",
        help="If set, keep at most one question per target_chunk_id before sampling "
        "(you generated 2 per chunk; this avoids near-duplicate questions eating your budget).",
    )
    args = parser.parse_args()

    with open(args.ground_truth, "r", encoding="utf-8") as f:
        full_set = json.load(f)

    print(f"Loaded {len(full_set)} ground truth items from {args.ground_truth}")

    pool = full_set
    if args.one_per_chunk:
        seen_chunks = set()
        deduped = []
        for item in full_set:
            chunk_id = item.get("target_chunk_id")
            if chunk_id not in seen_chunks:
                seen_chunks.add(chunk_id)
                deduped.append(item)
        pool = deduped
        print(f"After --one-per-chunk dedup: {len(pool)} items ({len(full_set) - len(pool)} dropped)")

    if args.sample_size >= len(pool):
        print(f"Sample size {args.sample_size} >= pool size {len(pool)}; using the full pool.")
        sample = pool
    else:
        rng = random.Random(args.seed)
        sample = rng.sample(pool, args.sample_size)

    # Give each item a stable index for later checkpointing/resuming.
    for i, item in enumerate(sample):
        item["_sample_id"] = i

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(sample, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Wrote {len(sample)} sampled items to {out_path} (seed={args.seed})")


if __name__ == "__main__":
    main()