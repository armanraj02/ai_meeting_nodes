from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from sqlalchemy.orm import Session

from backend.core.workflow_manager import WorkflowManager
from backend.database.models import Task as TaskModel, Meeting
from backend.integrations.github_integration import GitHubIntegration
from backend.integrations.jira_integration import JiraIntegration
from backend.integrations.trello_integration import TrelloIntegration
from backend.task_engine.task_schema import StructuredTask


router = APIRouter()


def get_db(request: Request):
    SessionLocal = request.app.state.SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/tasks")
def list_tasks(request: Request, meeting_id: int | None = None, db: Session = Depends(get_db)) -> dict[str, Any]:
    if meeting_id is None:
        meeting = db.query(Meeting).order_by(Meeting.id.desc()).first()
        if not meeting:
            return {"meeting_id": None, "tasks": []}
        meeting_id = meeting.id

    tasks = db.query(TaskModel).filter(TaskModel.meeting_id == meeting_id).order_by(TaskModel.id.asc()).all()
    return {
        "meeting_id": meeting_id,
        "tasks": [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "priority": t.priority,
                "team": t.team,
                "source_context": t.source_context,
                "confidence_score": t.confidence_score,
                "workflow_provider": t.workflow_provider,
                "workflow_key": t.workflow_key,
                "workflow_url": t.workflow_url,
            }
            for t in tasks
        ],
    }


@router.post("/tasks/publish")
def publish_tasks(
    request: Request,
    provider: str = Form(...),
    meeting_id: int | None = Form(default=None),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    settings = request.app.state.settings

    if meeting_id is None:
        meeting = db.query(Meeting).order_by(Meeting.id.desc()).first()
        if not meeting:
            raise HTTPException(status_code=404, detail="No meetings found")
        meeting_id = meeting.id

    tasks = db.query(TaskModel).filter(TaskModel.meeting_id == meeting_id).order_by(TaskModel.id.asc()).all()
    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks found for meeting")

    wm = WorkflowManager(
        github=GitHubIntegration(token=settings.github_token, repo=settings.github_repo),
        jira=JiraIntegration(
            base_url=settings.jira_base_url,
            email=settings.jira_email,
            api_token=settings.jira_api_token,
            project_key=settings.jira_project_key,
        ),
        trello=TrelloIntegration(key=settings.trello_key, token=settings.trello_token, list_id=settings.trello_list_id),
    )

    structured = [
        StructuredTask(
            title=t.title,
            description=t.description,
            priority=t.priority,
            team=t.team,
            source_context=t.source_context,
            confidence_score=t.confidence_score,
        )
        for t in tasks
    ]
    tickets = wm.publish(provider=provider, tasks=structured)

    for t, ticket in zip(tasks, tickets):
        t.workflow_provider = ticket.provider
        t.workflow_key = ticket.key
        t.workflow_url = ticket.url
        db.add(t)
    db.commit()

    return {
        "meeting_id": meeting_id,
        "provider": provider,
        "created_workflow_tickets": [
            {"provider": x.provider, "key": x.key, "url": x.url, "dry_run": x.dry_run} for x in tickets
        ],
    }

