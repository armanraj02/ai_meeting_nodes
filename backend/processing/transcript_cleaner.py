from __future__ import annotations

import re

from backend.utils.helpers import normalize_text


class TranscriptCleaner:
    """Cleans transcripts while keeping engineering signal."""

    FILLER_RE = re.compile(r"\b(um+|uh+|like|you know|i mean)\b", re.IGNORECASE)
    TIMESTAMP_RE = re.compile(r"^\s*\[?\d{1,2}:\d{2}(:\d{2})?\]?\s*", re.MULTILINE)

    def clean(self, raw_text: str) -> str:
        s = normalize_text(raw_text)
        s = self.TIMESTAMP_RE.sub("", s)
        s = self.FILLER_RE.sub("", s)
        s = re.sub(r"\s{2,}", " ", s)
        return normalize_text(s)

