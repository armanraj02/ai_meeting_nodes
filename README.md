# Agentic Meeting AI (backend)

Production-style backend that turns meeting transcripts (or audio) into structured engineering tasks via a RAG + multi-agent pipeline and publishes them to developer workflow tools.

## Quickstart (local)

```bash
cd agentic-meeting-ai
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.app:app --reload
```

## Environment

Copy `.env.example` to `.env` and set values as needed. The system will still run without external LLM keys (it falls back to a deterministic local model for tests/demo).

## API

- `POST /meeting/upload`
- `POST /meeting/process`
- `GET /tasks`
- `POST /tasks/publish`
- `GET /summary`

Interactive docs at `/docs`.

## Tests

```bash
pytest -q
```

