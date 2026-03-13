from __future__ import annotations

from backend.utils.helpers import dedupe_preserve_order


class RiskAgent:
    """Identifies risks, blockers, and unknowns."""

    name = "RiskAgent"

    def __init__(self):
        self.model = None

    def initialize(self, model):
        self.model = model
        return self

    def run(self, input_data: dict) -> dict:
        transcript = input_data.get("transcript", "")
        context = input_data.get("context", "")
        prompt = (
            "You are RiskAgent. Identify risks, blockers, and unknowns.\n"
            "Return JSON with key 'risks' (list of strings).\n\n"
            f"CONTEXT:\n{context}\n\nTRANSCRIPT:\n{transcript}\n"
        )
        out = self.model.generate_json(prompt, required_keys=["risks"])
        risks = [str(r).strip() for r in out.get("risks", []) if str(r).strip()]
        return {"risks": dedupe_preserve_order(risks)}

