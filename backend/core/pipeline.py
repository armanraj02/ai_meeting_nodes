from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

import httpx
from sqlalchemy.orm import Session

from backend.config import Settings
from backend.core.orchestrator import Orchestrator
from backend.database.models import Meeting, Transcript, AgentOutput, Decision, Task
from backend.processing.transcript_cleaner import TranscriptCleaner
from backend.processing.text_chunker import TextChunker
from backend.processing.meeting_segmenter import MeetingSegmenter
from backend.rag.context_pipeline import ContextPipeline
from backend.task_engine.task_structurer import TaskStructurer
from backend.task_engine.task_validator import TaskValidator
from backend.task_engine.task_schema import StructuredTask
from backend.utils.helpers import normalize_text
from backend.utils.logger import get_logger


logger = get_logger(__name__)


class LLMModel:
    """Minimal LLM interface used by agents."""

    def generate_json(self, prompt: str, *, required_keys: list[str]) -> dict[str, Any]:
        raise NotImplementedError


class DeterministicLocalModel(LLMModel):
    """
    Local deterministic model used when no external LLM is configured.

    It uses simple heuristics to extract topics/decisions/tasks/risks so the full
    pipeline is runnable and testable offline.
    """

    BULLET_RE = re.compile(r"^\s*[-*]\s+(.*)$")
    DECISION_RE = re.compile(r"\b(decision|we decided|agree|agreed)\b", re.IGNORECASE)
    RISK_RE = re.compile(r"\b(risk|blocker|blocked|concern|unknown|dependency)\b", re.IGNORECASE)
    TOPIC_HINT_RE = re.compile(r"\b(api|database|auth|login|security|performance|frontend|backend|deploy|ci|tests)\b", re.IGNORECASE)

    def _lines(self, prompt: str) -> list[str]:
        # transcript is usually appended after "TRANSCRIPT:"
        if "TRANSCRIPT:" in prompt:
            prompt = prompt.split("TRANSCRIPT:", 1)[1]
        s = normalize_text(prompt)
        return [ln.strip() for ln in s.split("\n") if ln.strip()]

    def generate_json(self, prompt: str, *, required_keys: list[str]) -> dict[str, Any]:
        text_lines = self._lines(prompt)
        joined = "\n".join(text_lines)

        out: dict[str, Any] = {}
        if "topics" in required_keys:
            topics: list[str] = []
            for ln in text_lines:
                m = self.BULLET_RE.match(ln)
                cand = (m.group(1) if m else ln)[:120]
                if self.TOPIC_HINT_RE.search(cand):
                    topics.append(cand)
            if not topics:
                topics = ["Engineering updates", "Planning & next steps"]
            out["topics"] = topics[:8]

        if "decisions" in required_keys:
            dec: list[str] = []
            for ln in text_lines:
                if self.DECISION_RE.search(ln):
                    dec.append(ln[:240])
            out["decisions"] = dec[:12]

        if "tasks" in required_keys:
            tasks: list[str] = []
            action_verbs = [
                "implement",
                "fix",
                "investigate",
                "analyze",
                "optimize",
                "reduce",
                "add",
                "build",
                "create",
                "set up",
                "ensure",
                "update",
                "retry",
            ]
            for ln in text_lines:
                low = ln.lower()
                m = self.BULLET_RE.match(ln)
                # 1) Explicit bullets or TODO-style prefixes
                if m:
                    tasks.append(m.group(1)[:240])
                    continue
                if low.startswith(("todo", "action", "next step")):
                    tasks.append(ln[:240])
                    continue
                # 2) Sentences assigning work: "X, can you ...", "Please ..."
                if "can you" in low or low.strip().startswith(("please", "let's add a task", "lets add a task")):
                    # Try to keep the part after "can you"/"please"
                    part = ln
                    for marker in ["can you", "Can you", "CAN YOU", "please", "Please", "PLEASE"]:
                        if marker in part:
                            part = part.split(marker, 1)[1]
                            break
                    tasks.append(part.strip().rstrip(".")[:240])
                    continue
                # 3) Lines mentioning "task" explicitly
                if "task" in low and ("add" in low or "implement" in low or "create" in low or "build" in low):
                    tasks.append(ln.strip().rstrip(".")[:240])
                    continue
                # 4) Speaker lines like "Name: do X" with action verbs
                if ":" in ln:
                    speaker, rest = ln.split(":", 1)
                    rest_low = rest.lower()
                    if any(v in rest_low for v in action_verbs):
                        tasks.append(rest.strip().rstrip(".")[:240])
                        continue
            out["tasks"] = tasks[:20]

        if "risks" in required_keys:
            risks: list[str] = []
            for ln in text_lines:
                if self.RISK_RE.search(ln):
                    risks.append(ln[:240])
            out["risks"] = risks[:15]

        if "expanded_tasks" in required_keys:
            # Expand by adding "define acceptance criteria" etc.
            base_tasks = []
            for ln in text_lines:
                m = self.BULLET_RE.match(ln)
                if m:
                    base_tasks.append(m.group(1))
            expanded: list[str] = []
            for t in base_tasks[:20]:
                if len(t.split()) < 4 or any(w in t.lower() for w in ["improve", "enhance", "update", "fix"]):
                    expanded.extend(
                        [
                            f"Define acceptance criteria for: {t}",
                            f"Add tests for: {t}",
                            f"Implement and document changes for: {t}",
                        ]
                    )
            out["expanded_tasks"] = expanded[:40]

        return out


class OpenAIChatModel(LLMModel):
    def __init__(self, *, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def generate_json(self, prompt: str, *, required_keys: list[str]) -> dict[str, Any]:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        schema_hint = {"type": "object", "properties": {k: {"type": "array"} for k in required_keys}, "required": required_keys}
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "Return only valid JSON."},
                {"role": "user", "content": prompt + "\n\nJSON schema hint:\n" + json.dumps(schema_hint)},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }
        with httpx.Client(timeout=40) as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
        content = data["choices"][0]["message"]["content"]
        try:
            obj = json.loads(content)
        except Exception:
            obj = {}
        for k in required_keys:
            obj.setdefault(k, [])
        return obj


@dataclass
class PipelineResult:
    meeting_id: int
    meeting_summary: str
    decisions: list[str]
    extracted_tasks: list[StructuredTask]
    risks: list[str]
    created_workflow_tickets: list[dict[str, Any]]


class Pipeline:
    """Defines and executes the complete pipeline."""

    def __init__(self, *, settings: Settings, context_pipeline: ContextPipeline):
        self.settings = settings
        self.context_pipeline = context_pipeline
        self.cleaner = TranscriptCleaner()
        self.segmenter = MeetingSegmenter()
        self.chunker = TextChunker()
        self.structurer = TaskStructurer()
        self.validator = TaskValidator()

        if settings.openai_api_key:
            self.model: LLMModel = OpenAIChatModel(api_key=settings.openai_api_key, model=settings.openai_model)
        else:
            self.model = DeterministicLocalModel()

        self.orchestrator = Orchestrator(self.model)

    def run(self, *, db: Session, meeting: Meeting) -> PipelineResult:
        if not meeting.transcript:
            meeting.transcript = db.query(Transcript).filter(Transcript.meeting_id == meeting.id).one_or_none()
        if not meeting.transcript:
            raise ValueError("Meeting has no transcript")

        raw = meeting.transcript.raw_text
        cleaned = self.cleaner.clean(raw)
        meeting.transcript.cleaned_text = cleaned
        db.add(meeting.transcript)
        db.commit()

        segments = self.segmenter.segment(cleaned)
        chunks = self.chunker.chunk(cleaned)
        self.context_pipeline.upsert_transcript_chunks(meeting_id=meeting.id, chunks=chunks)

        query = "engineering meeting summary, decisions, tasks, risks"
        ctx = self.context_pipeline.retrieve_context(query=query, k=6).context_text

        agent_result = self.orchestrator.run(transcript="\n\n".join(segments) if segments else cleaned, context=ctx)

        for agent_name, output_json in agent_result.agent_outputs.items():
            db.add(AgentOutput(meeting_id=meeting.id, agent_name=agent_name, output_json=output_json))

        for d in agent_result.decisions:
            db.add(Decision(meeting_id=meeting.id, text=d))

        structured = [self.structurer.structure(t, source_context=ctx) for t in agent_result.tasks]
        validation = self.validator.validate(structured)
        if validation.errors:
            logger.info("Task validation errors", extra={"extra": {"stage": "task_validation", "errors": validation.errors}})

        db.query(Task).filter(Task.meeting_id == meeting.id).delete()
        for st in validation.valid_tasks:
            db.add(
                Task(
                    meeting_id=meeting.id,
                    title=st.title,
                    description=st.description,
                    priority=st.priority,
                    team=st.team,
                    source_context=st.source_context,
                    confidence_score=st.confidence_score,
                )
            )

        db.commit()

        summary = self._summarize(agent_result, cleaned)

        return PipelineResult(
            meeting_id=meeting.id,
            meeting_summary=summary,
            decisions=agent_result.decisions,
            extracted_tasks=validation.valid_tasks,
            risks=agent_result.risks,
            created_workflow_tickets=[],
        )

    def _summarize(self, agent_result, cleaned_text: str) -> str:
        topics = agent_result.topics[:6]
        decisions = agent_result.decisions[:6]
        tasks = agent_result.tasks[:8]
        parts: list[str] = []
        if topics:
            parts.append("Topics: " + ", ".join(topics))
        if decisions:
            parts.append("Decisions: " + "; ".join(decisions))
        if tasks:
            parts.append("Top tasks: " + "; ".join(tasks))
        if not parts:
            return cleaned_text[:500]
        return "\n".join(parts)

