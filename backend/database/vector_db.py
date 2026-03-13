from __future__ import annotations

from backend.config import Settings
from backend.rag.vector_store import SqliteVectorStore


def get_vector_store(settings: Settings) -> SqliteVectorStore:
    return SqliteVectorStore(persist_dir=settings.chroma_persist_dir, collection_name=settings.rag_collection)

