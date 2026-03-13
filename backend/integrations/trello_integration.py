from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from backend.utils.helpers import stable_id
from backend.utils.logger import get_logger


logger = get_logger(__name__)


@dataclass
class TrelloIntegration:
    key: str | None
    token: str | None
    list_id: str | None

    def create_task(self, task_data: dict[str, Any]):
        from backend.core.workflow_manager import PublishedTicket

        name = str(task_data.get("title") or "Untitled task")
        desc = str(task_data.get("description") or "")
        if task_data.get("source_context"):
            desc = (desc + "\n\n" if desc else "") + "Source context:\n" + str(task_data["source_context"])

        if not (self.key and self.token and self.list_id):
            key = stable_id("trello", name)[:12]
            logger.info("Trello dry-run create_task", extra={"extra": {"stage": "publish", "provider": "trello", "dry_run": True, "name": name}})
            return PublishedTicket(provider="trello", key=key, url=None, dry_run=True)

        url = "https://api.trello.com/1/cards"
        params = {"key": self.key, "token": self.token, "idList": self.list_id, "name": name, "desc": desc[:8000]}
        with httpx.Client(timeout=20) as client:
            resp = client.post(url, params=params)
            resp.raise_for_status()
            data = resp.json()
        logger.info("Trello card created", extra={"extra": {"stage": "publish", "provider": "trello", "dry_run": False, "id": data.get("id")}})
        return PublishedTicket(provider="trello", key=str(data.get("id")), url=str(data.get("url")), dry_run=False)

