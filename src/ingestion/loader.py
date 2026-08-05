from pathlib import Path

def load_hmn_data():
    docs_dir = Path("hmn_engineering_docs")

    documents = []

    for md_file in docs_dir.glob("*.md"):
        parts = md_file.stem.split("_")

        documents.append({
            "id": md_file.stem,
            "category": parts[0],
            "subcategory": "_".join(parts[1:-1]) if len(parts) > 2 else None,
            "title": parts[-1].replace("-", " ").title(),
            "text": md_file.read_text(encoding="utf-8"),
            "source": md_file.name
        })

    return documents