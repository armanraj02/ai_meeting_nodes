from __future__ import annotations

from backend.rag.vector_store import SqliteVectorStore


def test_rag_can_upsert_and_query(tmp_path):
    store = SqliteVectorStore(persist_dir=str(tmp_path / "vec"), collection_name="test")
    store.upsert_texts(
        ids=["a", "b"],
        texts=["We use FastAPI for the backend.", "Chroma stores embeddings for retrieval."],
        metadatas=[{"type": "doc", "path": "a.md"}, {"type": "doc", "path": "b.md"}],
    )
    docs = store.query(text="How do we store embeddings?", n_results=2)
    assert len(docs) >= 1
    assert any("Chroma" in d.text for d in docs)

