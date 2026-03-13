from __future__ import annotations

from dataclasses import dataclass

from backend.integrations.github_integration import GitHubIntegration
from backend.integrations.jira_integration import JiraIntegration
from backend.integrations.trello_integration import TrelloIntegration
from backend.task_engine.task_schema import StructuredTask
from backend.utils.logger import get_logger


logger = get_logger(__name__)


@dataclass
class PublishedTicket:
    provider: str
    key: str | None
    url: str | None
    dry_run: bool


class WorkflowManager:
    def __init__(self, *, github: GitHubIntegration | None = None, jira: JiraIntegration | None = None, trello: TrelloIntegration | None = None):
        self.github = github
        self.jira = jira
        self.trello = trello

    def publish(self, *, provider: str, tasks: list[StructuredTask]) -> list[PublishedTicket]:
        provider = provider.lower().strip()
        if provider == "github":
            if not self.github:
                raise ValueError("GitHub integration is not configured")
            return [self.github.create_task(t.model_dump()) for t in tasks]
        if provider == "jira":
            if not self.jira:
                raise ValueError("Jira integration is not configured")
            return [self.jira.create_task(t.model_dump()) for t in tasks]
        if provider == "trello":
            if not self.trello:
                raise ValueError("Trello integration is not configured")
            return [self.trello.create_task(t.model_dump()) for t in tasks]
        raise ValueError(f"Unsupported provider '{provider}'")

