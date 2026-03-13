from __future__ import annotations

from backend.utils.constants import DEFAULT_CHUNK_OVERLAP, DEFAULT_CHUNK_SIZE
from backend.utils.helpers import normalize_text


class TextChunker:
    def __init__(self, *, chunk_size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        s = normalize_text(text)
        if not s:
            return []
        chunks: list[str] = []
        start = 0
        n = len(s)
        while start < n:
            end = min(n, start + self.chunk_size)
            # try to cut on paragraph boundary
            cut = s.rfind("\n\n", start, end)
            if cut != -1 and cut > start + 200:
                end = cut
            chunk = s[start:end].strip()
            if chunk:
                chunks.append(chunk)
            if end >= n:
                break
            start = max(0, end - self.overlap)
        return chunks

