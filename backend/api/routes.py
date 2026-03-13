from __future__ import annotations

from fastapi import APIRouter

from backend.api.meeting_routes import router as meeting_router
from backend.api.task_routes import router as task_router
from backend.api.integration_routes import router as integration_router


api_router = APIRouter()
api_router.include_router(meeting_router, tags=["meeting"])
api_router.include_router(task_router, tags=["tasks"])
api_router.include_router(integration_router, tags=["integrations"])

