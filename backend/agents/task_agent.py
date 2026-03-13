from __future__ import annotations

from backend.utils.helpers import dedupe_preserve_order


class TaskAgent:
    """Extracts action items / tasks from the meeting."""

    name = "TaskAgent"

    def __init__(self):
        self.model = None

    def initialize(self, model):
        self.model = model
        return self

    def run(self, input_data: dict) -> dict:
        transcript = input_data.get("transcript", "")
        context = input_data.get("context", "")
        prompt = (
            "You are TaskAgent. Extract engineering tasks/action items.\n"
            "Return JSON with key 'tasks' (list of strings). Make tasks imperative.\n\n"
            f"CONTEXT:\n{context}\n\nTRANSCRIPT:\n{transcript}\n"
        )
        out = self.model.generate_json(prompt, required_keys=["tasks"])
        tasks = [str(t).strip() for t in out.get("tasks", []) if str(t).strip()]
        return {"tasks": dedupe_preserve_order(tasks)}

