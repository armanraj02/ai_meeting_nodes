from __future__ import annotations

from typing import Any

from sqlalchemy import String, Text, Float, DateTime, ForeignKey, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from backend.database.database import Base


class Meeting(Base):
    __tablename__ = "meetings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now())
    title: Mapped[str] = mapped_column(String(255), default="Engineering meeting")
    source_type: Mapped[str] = mapped_column(String(50), default="transcript")  # transcript|audio
    source_uri: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    transcript: Mapped["Transcript"] = relationship(back_populates="meeting", uselist=False)
    agent_outputs: Mapped[list["AgentOutput"]] = relationship(back_populates="meeting")
    tasks: Mapped[list["Task"]] = relationship(back_populates="meeting")
    decisions: Mapped[list["Decision"]] = relationship(back_populates="meeting")


class Transcript(Base):
    __tablename__ = "transcripts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id"), unique=True)
    created_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now())
    raw_text: Mapped[str] = mapped_column(Text)
    cleaned_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    meeting: Mapped[Meeting] = relationship(back_populates="transcript")


class AgentOutput(Base):
    __tablename__ = "agent_outputs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id"))
    created_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now())
    agent_name: Mapped[str] = mapped_column(String(100))
    output_json: Mapped[dict[str, Any]] = mapped_column(JSON)

    meeting: Mapped[Meeting] = relationship(back_populates="agent_outputs")


class Decision(Base):
    __tablename__ = "decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id"))
    created_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now())
    text: Mapped[str] = mapped_column(Text)

    meeting: Mapped[Meeting] = relationship(back_populates="decisions")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id"))
    created_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now())

    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    team: Mapped[str] = mapped_column(String(50), default="engineering")
    source_context: Mapped[str] = mapped_column(Text, default="")
    confidence_score: Mapped[float] = mapped_column(Float, default=0.65)

    workflow_provider: Mapped[str | None] = mapped_column(String(40), nullable=True)
    workflow_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    workflow_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    meeting: Mapped[Meeting] = relationship(back_populates="tasks")

