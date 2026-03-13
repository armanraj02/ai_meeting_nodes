from __future__ import annotations

from backend.core.pipeline import DeterministicLocalModel
from backend.core.orchestrator import Orchestrator


def test_agents_produce_expected_keys():
    model = DeterministicLocalModel()
    orch = Orchestrator(model)
    transcript = """
    Topic: API auth
    - Add rate limiting to login
    Decision: We agreed to use JWT rotation.
    Risk: dependency on gateway team
    """
    res = orch.run(transcript=transcript, context="")
    assert isinstance(res.topics, list)
    assert isinstance(res.decisions, list)
    assert isinstance(res.tasks, list)
    assert isinstance(res.risks, list)
    assert "TopicAgent" in res.agent_outputs
    assert "DecisionAgent" in res.agent_outputs
    assert "TaskAgent" in res.agent_outputs
    assert "RiskAgent" in res.agent_outputs
    assert "RecursiveReasoner" in res.agent_outputs

