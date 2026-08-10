"""Quick sanity check: how many generations came back as internal errors
rather than real answers, before spending judge-model calls on them."""
# python src.evaluation.check_generations eval_data/generations.json

import json
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "eval_data/generations.json"

with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Total: {len(data)}")

by_stop_reason = {}
for item in data:
    reason = item.get("stop_reason") or "completed"
    by_stop_reason[reason] = by_stop_reason.get(reason, 0) + 1

print("\nBy stop_reason:")
for reason, count in sorted(by_stop_reason.items(), key=lambda x: -x[1]):
    print(f"  {reason}: {count}")

errors = [item for item in data if item.get("stop_reason") not in (None, "completed")]
if errors:
    print(f"\n{len(errors)} item(s) with non-'completed' stop_reason (check these before judging):")
    for item in errors:
        print(f"  [{item['_sample_id']}] {item['question'][:70]!r} -> {item.get('stop_reason')}")

no_tool = [item for item in data if not item.get("tool_calls")]
print(f"\n{len(no_tool)} item(s) where NO tool was called at all.")