from __future__ import annotations

from backend.config import Settings
from backend.core.pipeline import Pipeline
from backend.database.database import create_session_factory, Base
from backend.database.models import Meeting, Transcript, Task
from backend.database.vector_db import get_vector_store
from backend.rag.context_pipeline import ContextPipeline


def test_pipeline_end_to_end(tmp_path):
    settings = Settings(
        database_url="sqlite:///:memory:",
        chroma_persist_dir=str(tmp_path / "chroma"),
        rag_collection="test_collection",
        openai_api_key=None,
    )
    engine, SessionLocal = create_session_factory(settings.database_url)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        meeting = Meeting(title="Test meeting", source_type="transcript")
        db.add(meeting)
        db.commit()
        db.refresh(meeting)
        db.add(
            Transcript(
                meeting_id=meeting.id,
                raw_text="""
                Topic: Login security
                - Improve login security
                Decision: We agreed to add rate limiting.
                Risk: Possible false positives on CAPTCHA.
                """,
            )
        )
        db.commit()
        db.refresh(meeting)

        store = get_vector_store(settings)
        ctx = ContextPipeline(store)
        pipe = Pipeline(settings=settings, context_pipeline=ctx)
        result = pipe.run(db=db, meeting=meeting)

        assert result.meeting_id == meeting.id
        assert result.extracted_tasks
        saved = db.query(Task).filter(Task.meeting_id == meeting.id).all()
        assert len(saved) == len(result.extracted_tasks)
    finally:
        db.close()
        engine.dispose()

