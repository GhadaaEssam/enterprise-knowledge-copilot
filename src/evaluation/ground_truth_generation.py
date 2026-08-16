"""Generate retrieval ground truth from chunked ingestion documents.

Run with ``uv run python -m src.evaluation.ground_truth_generation``.
The script resumes from its output file after interruptions or rate limits.
"""

import argparse
import json
import os
import re
import time
from pathlib import Path

from dotenv import load_dotenv
from tqdm import tqdm

# run command: uv run python -m src.evaluation.ground_truth_generation

# Simple, fast chat model without internal reasoning overhead
MODEL_NAME = "llama-3.1-8b-instant"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "hmn_engineering_docs" / "chunked_documents.json"
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "data" / "ground_truth.json"

PROMPT_TEMPLATE = """You are an AI assistant helping generate evaluation data.
Based on the text below, generate exactly 2 concise, human-like questions answered directly by the content.

Return ONLY a raw JSON array of 2 strings: ["Question 1?", "Question 2?"]

Text:
{text}"""

def clean_and_parse_json(raw_text: str) -> list:
    if not raw_text or not raw_text.strip():
        raise ValueError("Model returned an empty response string.")

    raw_text = raw_text.strip()

    # 1. Strip markdown code fences
    if "```" in raw_text:
        raw_text = re.sub(r"```(?:json)?\s*(.*?)\s*```", r"\1", raw_text, flags=re.DOTALL).strip()

    # 2. Isolate array bracket content
    match = re.search(r"\[(.*)\]", raw_text, flags=re.DOTALL)
    if match:
        raw_text = f"[{match.group(1)}]"

    # 3. Standard JSON parse
    try:
        parsed = json.loads(raw_text)
        if isinstance(parsed, list) and len(parsed) > 0:
            return [str(q).strip() for q in parsed]
    except Exception:
        pass

    # 4. Escape raw backslashes (PHP namespaces)
    fixed_backslashes = re.sub(r'(?<!\\)\\(?!["\\/bfnrtu])', r'\\\\', raw_text)
    try:
        parsed = json.loads(fixed_backslashes)
        if isinstance(parsed, list) and len(parsed) > 0:
            return [str(q).strip() for q in parsed]
    except Exception:
        pass

    # 5. Extract questions directly using regex when interior double quotes are unescaped
    # Matches strings that start and end near quotes/commas/brackets
    extracted_questions = re.findall(r'"([^"\n]{10,}\??)"', raw_text)
    if extracted_questions:
        return [q.strip() for q in extracted_questions if len(q.strip()) > 5]

    raise ValueError(f"Could not parse JSON array from raw text: {raw_text[:60]}")

def load_existing_checkpoint(output_path: Path):
    if output_path.exists():
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                records = json.load(f)
            processed_ids = {item["target_chunk_id"] for item in records if "target_chunk_id" in item}
            return records, processed_ids
        except Exception:
            pass
    return [], set()


def save_checkpoint(records: list, output_path: Path):
    temp_path = output_path.with_suffix(".tmp")
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    temp_path.replace(output_path)


def generate_ground_truth_with_checkpointing(
    chunks: list, 
    llm_client, 
    output_path: Path, 
    delay_seconds: float = 1.0,
    max_chunk_chars: int = 1000
):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    ground_truth_records, processed_chunk_ids = load_existing_checkpoint(output_path)
    remaining_chunks = [c for c in chunks if c["chunk_id"] not in processed_chunk_ids]

    print(f"Total chunks: {len(chunks)} | Completed: {len(processed_chunk_ids)} | Remaining: {len(remaining_chunks)}")

    if not remaining_chunks:
        print("All chunks have already been processed!")
        return ground_truth_records

    for chunk in tqdm(remaining_chunks, desc="Generating Ground Truth"):
        chunk_id = chunk["chunk_id"]
        truncated_text = chunk.get("text", "")[:max_chunk_chars]
        prompt = PROMPT_TEMPLATE.format(text=truncated_text)

        try:
            # Standard chat completion call
            response = llm_client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.3
            )

            raw_content = response.choices[0].message.content
            questions = clean_and_parse_json(raw_content)

            for q in questions:
                ground_truth_records.append({
                    "question": q,
                    "target_chunk_id": chunk_id,
                    "target_document_id": chunk.get("document_id", ""),
                    "expected_output": chunk.get("text", ""),
                })

            processed_chunk_ids.add(chunk_id)
            save_checkpoint(ground_truth_records, output_path)

        except Exception as e:
            print(f"\nSkipped '{chunk_id}' -> Error: {e}")

        time.sleep(delay_seconds)

    return ground_truth_records


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate question-to-chunk ground truth from chunked documents."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT_PATH,
        help=f"Chunk JSON input (default: {DEFAULT_INPUT_PATH})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help=f"Checkpoint/output JSON (default: {DEFAULT_OUTPUT_PATH})",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Seconds to wait between API requests (default: 1.0).",
    )
    parser.add_argument(
        "--max-chunk-chars",
        type=int,
        default=1000,
        help="Maximum characters from each chunk sent to the model (default: 1000).",
    )
    args = parser.parse_args()

    if args.delay < 0:
        parser.error("--delay must be zero or greater")
    if args.max_chunk_chars < 1:
        parser.error("--max-chunk-chars must be greater than zero")
    if not args.input.exists():
        parser.error(f"Input chunk file does not exist: {args.input}")

    with args.input.open(encoding="utf-8") as file:
        chunks = json.load(file)
    if not isinstance(chunks, list) or not chunks:
        parser.error("Input chunk file must contain a non-empty JSON list")

    load_dotenv()
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        parser.error("GROQ_API_KEY is not set. Add it to .env or your environment.")

    from groq import Groq

    records = generate_ground_truth_with_checkpointing(
        chunks,
        Groq(api_key=api_key),
        args.output,
        delay_seconds=args.delay,
        max_chunk_chars=args.max_chunk_chars,
    )

    print(f"Saved {len(records)} ground-truth records to {args.output}")


if __name__ == "__main__":
    main()