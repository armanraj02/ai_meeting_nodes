from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session

from backend.core.pipeline import Pipeline
from backend.database.models import Meeting, Transcript, Task as TaskModel
from backend.database.vector_db import get_vector_store
from backend.rag.context_pipeline import ContextPipeline
from backend.utils.logger import get_logger


logger = get_logger(__name__)
router = APIRouter()


def get_db(request: Request):
    SessionLocal = request.app.state.SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/meeting/upload")
async def upload_meeting(
    request: Request,
    transcript_text: str | None = Form(default=None),
    transcript_file: UploadFile | None = File(default=None),
    title: str | None = Form(default=None),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    if not transcript_text and not transcript_file:
        raise HTTPException(status_code=400, detail="Provide transcript_text or transcript_file")

    if transcript_file is not None:
        content = await transcript_file.read()
        transcript_text = content.decode("utf-8", errors="ignore")

    meeting = Meeting(title=title or "Engineering meeting", source_type="transcript")
    db.add(meeting)
    db.commit()
    db.refresh(meeting)

    tr = Transcript(meeting_id=meeting.id, raw_text=transcript_text or "")
    db.add(tr)
    db.commit()

    logger.info("Meeting uploaded", extra={"extra": {"stage": "upload", "meeting_id": meeting.id}})
    return {"meeting_id": meeting.id, "status": "uploaded"}


@router.post("/meeting/process")
def process_meeting(
    request: Request,
    meeting_id: int = Form(...),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    meeting = db.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    if not meeting.transcript:
        meeting.transcript = db.query(Transcript).filter(Transcript.meeting_id == meeting_id).one_or_none()
    if not meeting.transcript:
        raise HTTPException(status_code=400, detail="Transcript not found for meeting")

    settings = request.app.state.settings
    store = get_vector_store(settings)
    ctx_pipe = ContextPipeline(store)
    pipeline = Pipeline(settings=settings, context_pipeline=ctx_pipe)

    result = pipeline.run(db=db, meeting=meeting)

    return {
        "meeting_id": result.meeting_id,
        "meeting_summary": result.meeting_summary,
        "decisions": result.decisions,
        "extracted_tasks": [t.model_dump() for t in result.extracted_tasks],
        "created_workflow_tickets": result.created_workflow_tickets,
        "risks": result.risks,
    }


@router.get("/summary")
def get_latest_summary(request: Request, db: Session = Depends(get_db)) -> dict[str, Any]:
    meeting = db.query(Meeting).order_by(Meeting.id.desc()).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="No meetings found")
    tasks = db.query(TaskModel).filter(TaskModel.meeting_id == meeting.id).order_by(TaskModel.id.asc()).all()
    decisions = [d.text for d in meeting.decisions] if meeting.decisions else []
    summary = meeting.transcript.cleaned_text if meeting.transcript and meeting.transcript.cleaned_text else (meeting.transcript.raw_text[:500] if meeting.transcript else "")
    return {
        "meeting_id": meeting.id,
        "meeting_summary": summary,
        "decisions": decisions,
        "extracted_tasks": [
            {
                "title": t.title,
                "description": t.description,
                "priority": t.priority,
                "team": t.team,
                "source_context": t.source_context,
                "confidence_score": t.confidence_score,
            }
            for t in tasks
        ],
        "created_workflow_tickets": [],
    }

