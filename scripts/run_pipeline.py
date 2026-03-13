from __future__ import annotations

import argparse

from backend.config import get_settings
from backend.core.pipeline import Pipeline
from backend.database.database import create_session_factory, Base
from backend.database.models import Meeting, Transcript
from backend.database.vector_db import get_vector_store
from backend.rag.context_pipeline import ContextPipeline


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--transcript", required=True, help="Path to transcript text file")
    ap.add_argument("--title", default="Engineering meeting")
    args = ap.parse_args()

    settings = get_settings()
    engine, SessionLocal = create_session_factory(settings.database_url)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        text = open(args.transcript, "r", encoding="utf-8", errors="ignore").read()
        m = Meeting(title=args.title, source_type="transcript", source_uri=args.transcript)
        db.add(m)
        db.commit()
        db.refresh(m)
        db.add(Transcript(meeting_id=m.id, raw_text=text))
        db.commit()

        store = get_vector_store(settings)
        ctx = ContextPipeline(store)
        pipe = Pipeline(settings=settings, context_pipeline=ctx)
        res = pipe.run(db=db, meeting=m)
        print(res.meeting_summary)
        print("\nTasks:")
        for t in res.extracted_tasks:
            print("-", t.title)
    finally:
        db.close()
        engine.dispose()


if __name__ == "__main__":
    main()

