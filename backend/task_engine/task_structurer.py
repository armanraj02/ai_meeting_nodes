from __future__ import annotations

from backend.task_engine.task_schema import StructuredTask
from backend.utils.helpers import normalize_text


class TaskStructurer:
    """Converts raw task strings into `StructuredTask` objects."""

    def structure(
        self,
        task_text: str,
        *,
        source_context: str = "",
        priority: str = "medium",
        team: str = "engineering",
        confidence_score: float = 0.65,
    ) -> StructuredTask:
        title = normalize_text(task_text)
        if len(title) > 255:
            title = title[:252] + "..."
        desc = ""
        if "\n" in task_text:
            parts = [p.strip() for p in task_text.split("\n") if p.strip()]
            title = parts[0][:255]
            if len(parts) > 1:
                desc = "\n".join(parts[1:])[:10_000]
        return StructuredTask(
            title=title,
            description=desc,
            priority=priority,
            team=team,
            source_context=normalize_text(source_context)[:10_000],
            confidence_score=float(confidence_score),
        )

