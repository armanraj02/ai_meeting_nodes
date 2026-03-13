from __future__ import annotations

from dataclasses import dataclass

from backend.task_engine.task_schema import StructuredTask
from backend.utils.helpers import dedupe_preserve_order, normalize_text


@dataclass
class ValidationResult:
    valid_tasks: list[StructuredTask]
    dropped_duplicates: int
    errors: list[str]


class TaskValidator:
    """Validates schema completeness and de-duplicates tasks."""

    def validate(self, tasks: list[StructuredTask]) -> ValidationResult:
        errors: list[str] = []
        normalized_titles = [normalize_text(t.title).lower() for t in tasks]
        deduped_titles = dedupe_preserve_order(normalized_titles)

        title_to_first: dict[str, StructuredTask] = {}
        for t in tasks:
            k = normalize_text(t.title).lower()
            title_to_first.setdefault(k, t)

        valid: list[StructuredTask] = []
        for k in deduped_titles:
            t = title_to_first[k]
            try:
                valid.append(StructuredTask(**t.model_dump()))
            except Exception as e:
                errors.append(f"Invalid task '{t.title}': {e}")

        dropped = max(0, len(tasks) - len(valid))
        return ValidationResult(valid_tasks=valid, dropped_duplicates=dropped, errors=errors)

