from __future__ import annotations

import re

from backend.utils.helpers import normalize_text


class MeetingSegmenter:
    """
    Light segmentation into agenda-like sections.

    This helps agents focus by giving them smaller windows (topics/decisions/tasks).
    """

    HEADER_RE = re.compile(r"^\s*(topic|agenda|decision|action item|actions)\s*[:\-]\s*", re.IGNORECASE)

    def segment(self, cleaned_text: str) -> list[str]:
        s = normalize_text(cleaned_text)
        if not s:
            return []
        lines = [ln.strip() for ln in s.split("\n") if ln.strip()]
        segments: list[str] = []
        buf: list[str] = []
        for ln in lines:
            if self.HEADER_RE.match(ln) and buf:
                segments.append("\n".join(buf).strip())
                buf = [ln]
            else:
                buf.append(ln)
        if buf:
            segments.append("\n".join(buf).strip())
        return segments

