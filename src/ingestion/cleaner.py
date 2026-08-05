import os
import json
import re
from pathlib import Path
from typing import Dict, Any, List

RAW_DIR = Path("data/raw/hmn_engineering_docs")
PROCESSED_DIR = Path("data/processed/hmn_engineering_docs")
OUTPUT_JSON = Path("data/processed/cleaned_documents.json")

def clean_rag_text(text: str) -> str:
    if not text:
        return ""

    # 1. Remove metadata headers & footers from scraper
    text = re.sub(r"^#\s+Source:\s+https?://\S+", "", text, flags=re.MULTILINE)
    text = re.sub(r"Accessed\s+[A-Za-z]{3},\s+\d{1,2}\s+[A-Za-z]{3}\s+\d{4}.*", "", text)
    text = re.sub(r"\[Made by Humans\]\(https?://\S+\)", "", text)

    # 2. Remove images & media
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)

    # 3. Clean heading anchor links & inline HTML tags
    text = re.sub(r"\[#\]\([^)]+\)", "", text)
    text = re.sub(r"<[^>]+>", "", text)

    # 4. Remove standalone navigation links
    text = re.sub(r"^\s*(\[?\b(Previous|Next)\b\]?\(.*?\)|«|»)\s*$", "", text, flags=re.IGNORECASE | re.MULTILINE)

    # 5. Mask code blocks to protect formatting
    code_blocks: List[str] = []
    def extract_code_block(match):
        code_blocks.append(match.group(0))
        return f"__CODE_BLOCK_{len(code_blocks) - 1}__"

    text = re.sub(r"```[\s\S]*?```", extract_code_block, text)

    # 6. Normalize whitespace and remove empty lines
    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        line = re.sub(r"[ \t]+", " ", line)
        if line:
            cleaned_lines.append(line)

    text = "\n".join(cleaned_lines)

    # 7. Restore code blocks
    for i, block in enumerate(code_blocks):
        text = text.replace(f"__CODE_BLOCK_{i}__", block)

    # 8. Unify quotes and special characters
    text = text.replace("“", '"').replace("”", '"').replace("’", "'").replace("–", "-")

    return text.strip()

def build_metadata_from_path(file_path: Path) -> Dict[str, Any]:
    """Derives ID, category, and subcategory from filename conventions."""
    stem = file_path.stem  # e.g., 'how-we-work_process_agile'
    parts = stem.split("_")
    
    category = parts[0] if len(parts) > 0 else "general"
    subcategory = parts[1] if len(parts) > 2 else None
    title = parts[-1].replace("-", " ").title()
    
    return {
        "id": stem,
        "category": category,
        "subcategory": subcategory,
        "title": title,
        "source": file_path.name
    }

def batch_clean_docs():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    raw_files = list(RAW_DIR.glob("*.md"))
    
    print(f"Found {len(raw_files)} raw files in {RAW_DIR}")
    
    cleaned_dataset = []
    
    for file_path in raw_files:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_text = f.read()
            
        cleaned_text = clean_rag_text(raw_text)
        metadata = build_metadata_from_path(file_path)
        metadata["text"] = cleaned_text
        
        # Save individual cleaned markdown file
        out_file = PROCESSED_DIR / file_path.name
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(cleaned_text)
            
        cleaned_dataset.append(metadata)
        
    # Save consolidated dataset as JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(cleaned_dataset, f, indent=2, ensure_ascii=False)
        
    print(f" Successfully processed {len(cleaned_dataset)} files.")
    print(f" Processed markdown files saved to: {PROCESSED_DIR}")
    print(f" Consolidated RAG JSON saved to: {OUTPUT_JSON}")

if __name__ == "__main__":
    batch_clean_docs()