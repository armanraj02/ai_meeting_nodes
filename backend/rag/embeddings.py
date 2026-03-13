from __future__ import annotations

import hashlib
from dataclasses import dataclass

import math
import random


@dataclass
class EmbeddingConfig:
    dim: int = 384


class DeterministicEmbedder:
    """
    Deterministic local embedder for demos/tests (no network).

    This is not a semantic model; it provides stable vectors so the RAG stack
    is fully functional without external keys.
    """

    def __init__(self, config: EmbeddingConfig | None = None):
        self.config = config or EmbeddingConfig()

    def embed(self, texts: list[str]) -> list[list[float]]:
        out: list[list[float]] = []
        for t in texts:
            h = hashlib.sha256(t.encode("utf-8", errors="ignore")).digest()
            seed = int.from_bytes(h[:8], "little", signed=False)
            rng = random.Random(seed)
            v = [rng.gauss(0.0, 1.0) for _ in range(self.config.dim)]
            norm = math.sqrt(sum(x * x for x in v)) or 1.0
            out.append([x / norm for x in v])
        return out

