from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import json
import math
import sqlite3
from pathlib import Path

from backend.rag.embeddings import DeterministicEmbedder


@dataclass
class RetrievedDoc:
    id: str
    text: str
    metadata: dict[str, Any]
    score: float | None = None


class SqliteVectorStore:
    """
    Pure-Python SQLite vector store.

    Stores embeddings as JSON arrays; performs cosine distance search in Python.
    This avoids native deps (NumPy/Chroma) and works on Windows without build tools.
    """

    def __init__(self, *, persist_dir: str, collection_name: str):
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        Path(persist_dir).mkdir(parents=True, exist_ok=True)
        self.db_path = str(Path(persist_dir) / f"{collection_name}.sqlite")
        self._conn = sqlite3.connect(self.db_path)
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
              id TEXT PRIMARY KEY,
              text TEXT NOT NULL,
              metadata TEXT NOT NULL,
              embedding TEXT NOT NULL
            )
            """
        )
        self._conn.commit()
        self._embedder = DeterministicEmbedder()

    def upsert_texts(self, *, ids: list[str], texts: list[str], metadatas: list[dict[str, Any]]):
        embeddings = self._embedder.embed(texts)
        rows = []
        for i in range(len(ids)):
            rows.append((ids[i], texts[i], json.dumps(metadatas[i] or {}), json.dumps(embeddings[i])))
        self._conn.executemany(
            "INSERT INTO documents(id, text, metadata, embedding) VALUES(?, ?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET text=excluded.text, metadata=excluded.metadata, embedding=excluded.embedding",
            rows,
        )
        self._conn.commit()

    def query(self, *, text: str, n_results: int = 6, where: dict[str, Any] | None = None) -> list[RetrievedDoc]:
        q = self._embedder.embed([text])[0]

        cur = self._conn.cursor()
        cur.execute("SELECT id, text, metadata, embedding FROM documents")
        candidates = cur.fetchall()

        filtered = []
        for doc_id, doc_text, meta_s, emb_s in candidates:
            meta = json.loads(meta_s) if meta_s else {}
            if where:
                ok = True
                for k, v in where.items():
                    if meta.get(k) != v:
                        ok = False
                        break
                if not ok:
                    continue
            emb = json.loads(emb_s)
            filtered.append((doc_id, doc_text, meta, emb))

        def cosine_distance(a: list[float], b: list[float]) -> float:
            dot = 0.0
            na = 0.0
            nb = 0.0
            for i in range(min(len(a), len(b))):
                dot += a[i] * b[i]
                na += a[i] * a[i]
                nb += b[i] * b[i]
            denom = (math.sqrt(na) * math.sqrt(nb)) or 1.0
            cos = dot / denom
            return 1.0 - cos

        scored = []
        for doc_id, doc_text, meta, emb in filtered:
            scored.append((cosine_distance(q, emb), doc_id, doc_text, meta))
        scored.sort(key=lambda x: x[0])

        out: list[RetrievedDoc] = []
        for dist, doc_id, doc_text, meta in scored[: max(1, n_results)]:
            out.append(RetrievedDoc(id=str(doc_id), text=str(doc_text), metadata=dict(meta), score=float(dist)))
        return out

