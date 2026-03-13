from __future__ import annotations

from backend.utils.helpers import dedupe_preserve_order


class TopicAgent:
    """Extracts meeting topics/themes."""

    name = "TopicAgent"

    def __init__(self):
        self.model = None

    def initialize(self, model):
        self.model = model
        return self

    def run(self, input_data: dict) -> dict:
        transcript = input_data.get("transcript", "")
        context = input_data.get("context", "")
        prompt = (
            "You are TopicAgent. Extract the main engineering topics discussed.\n"
            "Return JSON with key 'topics' (list of short strings).\n\n"
            f"CONTEXT:\n{context}\n\nTRANSCRIPT:\n{transcript}\n"
        )
        out = self.model.generate_json(prompt, required_keys=["topics"])
        topics = [str(t).strip() for t in out.get("topics", []) if str(t).strip()]
        return {"topics": dedupe_preserve_order(topics)}

