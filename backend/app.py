from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.config import get_settings
from backend.database.database import create_session_factory
from backend.database.database import Base
from backend.api.routes import api_router
from backend.utils.logger import get_logger


logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    engine, SessionLocal = create_session_factory(settings.database_url)
    Base.metadata.create_all(bind=engine)
    app.state.settings = settings
    app.state.engine = engine
    app.state.SessionLocal = SessionLocal
    logger.info("App startup complete", extra={"extra": {"stage": "startup"}})
    yield
    engine.dispose()
    logger.info("App shutdown complete", extra={"extra": {"stage": "shutdown"}})


app = FastAPI(title="Agentic Meeting AI", version="0.1.0", lifespan=lifespan)
app.include_router(api_router)

