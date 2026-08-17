import json
import re
from pathlib import Path
from typing import Dict, Any, List

# File Paths
INPUT_JSON = Path("data/processed/hmn_engineering_docs/cleaned_documents.json")
OUTPUT_JSON = Path("data/processed/hmn_engineering_docs/chunked_documents.json")

# Chunking Limits
MAX_CHUNK_CHAR_SIZE = 1200  # Fallback soft limit for very long sections
OVERLAP_CHAR_SIZE = 150     # Overlap when splitting oversized sections


def split_markdown_by_headers(text: str) -> List[Dict[str, str]]:
    """
    Splits markdown text into semantic sections based on ATX headings (# , ## , ### ).
    Preserves heading titles alongside their respective content blocks.
    """
    # Regex to capture Markdown headers: # Header, ## Header, etc.
    header_pattern = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)
    
    matches = list(header_pattern.finditer(text))
    if not matches:
        # No headings found; return entire text as a single section
        return [{"section_title": "Overview", "content": text.strip()}]

    sections = []
    
    # 1. Capture any intro text before the first heading
    if matches[0].start() > 0:
        intro_text = text[:matches[0].start()].strip()
        if intro_text:
            sections.append({
                "section_title": "Introduction",
                "content": intro_text
            })

    # 2. Iterate through matched headers and slice corresponding content
    for i, match in enumerate(matches):
        heading_title = match.group(2).strip()
        start_pos = match.start()
        
        # Determine section end boundary
        end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        
        section_content = text[start_pos:end_pos].strip()
        
        sections.append({
            "section_title": heading_title,
            "content": section_content
        })

    return sections


def split_oversized_text(text: str, max_size: int = MAX_CHUNK_CHAR_SIZE, overlap: int = OVERLAP_CHAR_SIZE) -> List[str]:
    """
    Fallback splitter for sections that exceed MAX_CHUNK_CHAR_SIZE,
    using line-aware sliding windows with overlap.
    """
    if len(text) <= max_size:
        return [text]

    lines = text.splitlines()
    sub_chunks = []
    current_chunk = []
    current_length = 0

    for line in lines:
        if current_length + len(line) > max_size and current_chunk:
            sub_chunks.append("\n".join(current_chunk))
            
            # Create overlap from the end of current chunk
            overlap_lines = []
            overlap_len = 0
            for prev_line in reversed(current_chunk):
                if overlap_len + len(prev_line) > overlap:
                    break
                overlap_lines.insert(0, prev_line)
                overlap_len += len(prev_line)
                
            current_chunk = overlap_lines
            current_length = overlap_len

        current_chunk.append(line)
        current_length += len(line) + 1

    if current_chunk:
        sub_chunks.append("\n".join(current_chunk))

    return sub_chunks


def chunk_documents(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Processes document objects into structured semantic chunks."""
    all_chunks = []

    for doc in documents:
        doc_id = doc.get("id", "doc")
        category = doc.get("category", "")
        doc_title = doc.get("title", "")
        source = doc.get("source", "")
        raw_text = doc.get("text", "")

        if not raw_text:
            continue

        # Split document by markdown headings
        sections = split_markdown_by_headers(raw_text)

        chunk_counter = 1
        for section in sections:
            section_content = section["content"]
            section_title = section["section_title"]

            # Handle oversized sections using sliding window fallback
            sub_sections = split_oversized_text(section_content)

            for sub_text in sub_sections:
                # Compound title preserves both document title and section heading
                compound_title = f"{doc_title} > {section_title}" if section_title != "Overview" else doc_title

                chunk_obj = {
                    "chunk_id": f"{doc_id}_chunk_{chunk_counter}",
                    "document_id": doc_id,
                    "title": compound_title,
                    "category": category,
                    "source": source,
                    "text": sub_text
                }
                
                all_chunks.append(chunk_obj)
                chunk_counter += 1

    return all_chunks


def main():
    if not INPUT_JSON.exists():
        print(f"Error: {INPUT_JSON} does not exist. Run batch_clean_docs() first.")
        return

    print(f"Loading cleaned documents from {INPUT_JSON}...")
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        documents = json.load(f)

    print(f"Chunking {len(documents)} documents...")
    chunked_data = chunk_documents(documents)

    # Save output JSON
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(chunked_data, f, indent=2, ensure_ascii=False)

    print(f"Successfully created {len(chunked_data)} chunks across {len(documents)} documents!")
    print(f"Chunked dataset saved to: {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
