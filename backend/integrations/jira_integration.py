from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from backend.utils.helpers import stable_id
from backend.utils.logger import get_logger


logger = get_logger(__name__)


@dataclass
class JiraIntegration:
    base_url: str | None
    email: str | None
    api_token: str | None
    project_key: str | None

    def create_task(self, task_data: dict[str, Any]):
        from backend.core.workflow_manager import PublishedTicket

        summary = str(task_data.get("title") or "Untitled task")
        description = str(task_data.get("description") or "")
        if task_data.get("source_context"):
            description = (description + "\n\n" if description else "") + "Source context:\n" + str(task_data["source_context"])

        if not (self.base_url and self.email and self.api_token and self.project_key):
            key = stable_id("jira", summary)[:12].upper()
            logger.info("Jira dry-run create_task", extra={"extra": {"stage": "publish", "provider": "jira", "dry_run": True, "summary": summary}})
            return PublishedTicket(provider="jira", key=key, url=None, dry_run=True)

        url = self.base_url.rstrip("/") + "/rest/api/3/issue"
        auth = (self.email, self.api_token)
        payload = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": summary,
                "issuetype": {"name": "Task"},
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [{"type": "paragraph", "content": [{"type": "text", "text": description[:5000]}]}],
                },
            }
        }
        with httpx.Client(timeout=25) as client:
            resp = client.post(url, auth=auth, json=payload)
            resp.raise_for_status()
            data = resp.json()
        issue_key = str(data.get("key"))
        browse = self.base_url.rstrip("/") + "/browse/" + issue_key
        logger.info("Jira issue created", extra={"extra": {"stage": "publish", "provider": "jira", "dry_run": False, "key": issue_key}})
        return PublishedTicket(provider="jira", key=issue_key, url=browse, dry_run=False)

