from __future__ import annotations

from backend.utils.helpers import dedupe_preserve_order


class DecisionAgent:
    """Extracts explicit decisions and agreements."""

    name = "DecisionAgent"

    def __init__(self):
        self.model = None

    def initialize(self, model):
        self.model = model
        return self

    def run(self, input_data: dict) -> dict:
        transcript = input_data.get("transcript", "")
        context = input_data.get("context", "")
        prompt = (
            "You are DecisionAgent. Extract decisions (what the team agreed to do).\n"
            "Return JSON with key 'decisions' (list of strings).\n\n"
            f"CONTEXT:\n{context}\n\nTRANSCRIPT:\n{transcript}\n"
        )
        out = self.model.generate_json(prompt, required_keys=["decisions"])
        decisions = [str(d).strip() for d in out.get("decisions", []) if str(d).strip()]
        return {"decisions": dedupe_preserve_order(decisions)}

