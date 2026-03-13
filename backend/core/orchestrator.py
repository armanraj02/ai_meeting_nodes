from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.agents.topic_agent import TopicAgent
from backend.agents.decision_agent import DecisionAgent
from backend.agents.task_agent import TaskAgent
from backend.agents.risk_agent import RiskAgent
from backend.agents.recursive_reasoner import RecursiveReasoner
from backend.utils.logger import get_logger


logger = get_logger(__name__)


@dataclass
class OrchestratorResult:
    topics: list[str]
    decisions: list[str]
    tasks: list[str]
    risks: list[str]
    agent_outputs: dict[str, dict[str, Any]]


class Orchestrator:
    """
    Orchestrator-based agent system.

    Order (required):
    TopicAgent -> DecisionAgent -> TaskAgent -> RiskAgent -> RecursiveReasoner
    """

    def __init__(self, model):
        self.model = model
        self.topic_agent = TopicAgent().initialize(model)
        self.decision_agent = DecisionAgent().initialize(model)
        self.task_agent = TaskAgent().initialize(model)
        self.risk_agent = RiskAgent().initialize(model)
        self.recursive_reasoner = RecursiveReasoner().initialize(model)

    def run(self, *, transcript: str, context: str = "") -> OrchestratorResult:
        agent_outputs: dict[str, dict[str, Any]] = {}

        t_out = self.topic_agent.run({"transcript": transcript, "context": context})
        agent_outputs[self.topic_agent.name] = t_out

        d_out = self.decision_agent.run({"transcript": transcript, "context": context})
        agent_outputs[self.decision_agent.name] = d_out

        task_out = self.task_agent.run({"transcript": transcript, "context": context})
        agent_outputs[self.task_agent.name] = task_out

        r_out = self.risk_agent.run({"transcript": transcript, "context": context})
        agent_outputs[self.risk_agent.name] = r_out

        rr_out = self.recursive_reasoner.run({"tasks": task_out.get("tasks", []), "context": context})
        agent_outputs[self.recursive_reasoner.name] = rr_out

        topics = list(t_out.get("topics", []))
        decisions = list(d_out.get("decisions", []))
        risks = list(r_out.get("risks", []))
        expanded_tasks = list(rr_out.get("expanded_tasks", task_out.get("tasks", [])))

        logger.info(
            "Orchestrator complete",
            extra={"extra": {"stage": "agents_complete", "topics": len(topics), "decisions": len(decisions), "tasks": len(expanded_tasks), "risks": len(risks)}},
        )
        return OrchestratorResult(
            topics=topics,
            decisions=decisions,
            tasks=expanded_tasks,
            risks=risks,
            agent_outputs=agent_outputs,
        )

