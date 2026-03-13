from __future__ import annotations

from pydantic import BaseModel, Field


class StructuredTask(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: str = Field(default="", max_length=10_000)
    priority: str = Field(default="medium")  # low|medium|high|critical
    team: str = Field(default="engineering")
    source_context: str = Field(default="", max_length=10_000)
    confidence_score: float = Field(default=0.65, ge=0.0, le=1.0)

    class Config:
        extra = "ignore"

