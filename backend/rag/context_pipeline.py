from __future__ import annotations

from dataclasses import dataclass

from backend.rag.retriever import Retriever
from backend.rag.vector_store import SqliteVectorStore, RetrievedDoc
from backend.utils.helpers import stable_id, normalize_text
from backend.utils.logger import get_logger


logger = get_logger(__name__)


@dataclass
class ContextResult:
    retrieved_docs: list[RetrievedDoc]
    context_text: str


class ContextPipeline:
    """
    RAG context pipeline:
    - upserts transcript chunks into vector store
    - retrieves relevant docs for a query
    - produces a consolidated context string for agents
    """

    def __init__(self, store: SqliteVectorStore):
        self.store = store
        self.retriever = Retriever(store)

    def upsert_transcript_chunks(self, *, meeting_id: int, chunks: list[str]):
        ids = [stable_id(f"meeting:{meeting_id}", f"chunk:{i}") for i in range(len(chunks))]
        metas = [{"type": "transcript_chunk", "meeting_id": meeting_id, "chunk_index": i} for i in range(len(chunks))]
        self.store.upsert_texts(ids=ids, texts=[normalize_text(c) for c in chunks], metadatas=metas)
        logger.info("Upserted transcript chunks", extra={"extra": {"stage": "rag_upsert", "meeting_id": meeting_id, "count": len(chunks)}})

    def retrieve_context(self, *, query: str, k: int = 6) -> ContextResult:
        docs = self.retriever.retrieve(query, k=k)
        ctx_parts: list[str] = []
        for d in docs:
            header = []
            if d.metadata.get("type"):
                header.append(str(d.metadata["type"]))
            if d.metadata.get("path"):
                header.append(str(d.metadata["path"]))
            if d.metadata.get("meeting_id") is not None:
                header.append(f"meeting_id={d.metadata.get('meeting_id')}")
            prefix = f"[{' | '.join(header)}]" if header else "[doc]"
            ctx_parts.append(prefix + "\n" + (d.text or "").strip())
        context_text = "\n\n---\n\n".join([p for p in ctx_parts if p.strip()])
        return ContextResult(retrieved_docs=docs, context_text=context_text)

