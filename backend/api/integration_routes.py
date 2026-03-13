from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request


router = APIRouter()


@router.get("/integrations/status")
def integrations_status(request: Request) -> dict[str, Any]:
    s = request.app.state.settings
    return {
        "github": {"configured": bool(s.github_token and s.github_repo), "repo": s.github_repo},
        "jira": {"configured": bool(s.jira_base_url and s.jira_email and s.jira_api_token and s.jira_project_key), "project": s.jira_project_key},
        "trello": {"configured": bool(s.trello_key and s.trello_token and s.trello_list_id), "list_id": s.trello_list_id},
    }

