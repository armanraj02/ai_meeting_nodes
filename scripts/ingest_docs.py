from __future__ import annotations

from pathlib import Path

from backend.config import get_settings
from backend.database.vector_db import get_vector_store
from backend.utils.helpers import stable_id


def main():
    settings = get_settings()
    store = get_vector_store(settings)
    docs_dir = Path("data/documents")
    docs_dir.mkdir(parents=True, exist_ok=True)

    paths = [p for p in docs_dir.rglob("*") if p.is_file() and p.suffix.lower() in {".md", ".txt"}]
    ids = [stable_id("doc", str(p)) for p in paths]
    texts = [p.read_text(encoding="utf-8", errors="ignore") for p in paths]
    metas = [{"type": "doc", "path": str(p)} for p in paths]
    if paths:
        store.upsert_texts(ids=ids, texts=texts, metadatas=metas)
    print(f"Ingested {len(paths)} documents into Chroma collection '{settings.rag_collection}'.")


if __name__ == "__main__":
    main()

