from __future__ import annotations

from pathlib import Path

from backend.utils.helpers import normalize_text


class TranscriptLoader:
    """Loads transcript text from direct input or file."""

    def load_from_text(self, text: str) -> str:
        return normalize_text(text)

    def load_from_file(self, path: str) -> str:
        p = Path(path)
        data = p.read_text(encoding="utf-8", errors="ignore")
        return normalize_text(data)

