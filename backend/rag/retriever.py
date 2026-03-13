from __future__ import annotations

from backend.rag.vector_store import SqliteVectorStore, RetrievedDoc
from backend.utils.constants import DEFAULT_MAX_CONTEXT_DOCS


class Retriever:
    def __init__(self, store: SqliteVectorStore):
        self.store = store

    def retrieve(self, query: str, *, k: int = DEFAULT_MAX_CONTEXT_DOCS) -> list[RetrievedDoc]:
        return self.store.query(text=query, n_results=k)

