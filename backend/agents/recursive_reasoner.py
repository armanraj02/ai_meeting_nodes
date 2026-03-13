from __future__ import annotations

from backend.utils.helpers import dedupe_preserve_order


class RecursiveReasoner:
    """
    Expands vague tasks into concrete technical subtasks/steps.
    """

    name = "RecursiveReasoner"

    def __init__(self):
        self.model = None

    def initialize(self, model):
        self.model = model
        return self

    def run(self, input_data: dict) -> dict:
        tasks: list[str] = input_data.get("tasks", []) or []
        context = input_data.get("context", "")
        prompt = (
            "You are RecursiveReasoner. Expand each task into more concrete subtasks.\n"
            "Return JSON with key 'expanded_tasks' (list of strings). Keep each item a task.\n\n"
            f"CONTEXT:\n{context}\n\nTASKS:\n" + "\n".join(f"- {t}" for t in tasks)
        )
        out = self.model.generate_json(prompt, required_keys=["expanded_tasks"])
        expanded = [str(t).strip() for t in out.get("expanded_tasks", []) if str(t).strip()]
        merged = dedupe_preserve_order([*tasks, *expanded])
        return {"expanded_tasks": merged}

