from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from backend.utils.helpers import stable_id
from backend.utils.logger import get_logger


logger = get_logger(__name__)


@dataclass
class GitHubIntegration:
    token: str | None
    repo: str | None  # "owner/name"

    def create_task(self, task_data: dict[str, Any]):
        from backend.core.workflow_manager import PublishedTicket

        title = str(task_data.get("title") or "Untitled task")
        body = str(task_data.get("description") or "")
        if task_data.get("source_context"):
            body = (body + "\n\n" if body else "") + "## Source context\n" + str(task_data["source_context"])

        if not self.token or not self.repo:
            key = stable_id("github", title)[:12]
            logger.info("GitHub dry-run create_task", extra={"extra": {"stage": "publish", "provider": "github", "dry_run": True, "title": title}})
            return PublishedTicket(provider="github", key=key, url=None, dry_run=True)

        url = f"https://api.github.com/repos/{self.repo}/issues"
        headers = {"Authorization": f"Bearer {self.token}", "Accept": "application/vnd.github+json"}
        payload = {"title": title, "body": body}
        with httpx.Client(timeout=20) as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
        logger.info("GitHub issue created", extra={"extra": {"stage": "publish", "provider": "github", "dry_run": False, "number": data.get("number")}})
        return PublishedTicket(provider="github", key=str(data.get("number")), url=str(data.get("html_url")), dry_run=False)

