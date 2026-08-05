from minsearch import Index
from sqlitesearch import TextSearchIndex
import time

def build_minsearch_index(documents):
    index = Index(
        text_fields=["text", "id"],
        keyword_fields=["category","subcategory"]
    )
    index.fit(documents)
    return index

def build_sqlitesearch_index(documents):
    index = TextSearchIndex(
        text_fields=["text", "id"],
        keyword_fields=["category","subcategory"],
        db_path="faq.db"
    )

    for doc in documents:
        index.add(doc)
        print(f"""Added: {doc["id"][:60]}...""")
        time.sleep(0.5)

    index.close()
    print("Done. Index saved to faq.db")

    return index