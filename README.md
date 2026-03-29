# 🤖 Agentic Meeting AI

Transform meeting transcripts into structured engineering tasks using AI agents and RAG.

---

## 📖 Project Overview

This project automates the extraction of actionable insights from meeting transcripts. Using a multi-agent architecture powered by Retrieval Augmented Generation (RAG), the system:

1. **Ingests** meeting audio files or text transcripts
2. **Processes** content through specialized AI agents
3. **Extracts** tasks, decisions, and risks
4. **Publishes** results to external tools (GitHub, Jira, Trello)

### Pipeline Flow:
- **Input Layer** → Audio capture, speech-to-text, transcript loading
- **Processing Layer** → Text cleaning, segmentation, chunking
- **RAG Pipeline** → Semantic embeddings, context retrieval
- **Agent Orchestration** → Decision, Task, Risk, Topic, and Recursive Reasoning agents
- **Task Engine** → Structuring and validation
- **Integration Layer** → GitHub, Jira, Trello publishing

---

## 🛠️ Technologies Used

| Component | Technology |
| :--- | :--- |
| **Framework** | FastAPI, Uvicorn |
| **Language** | Python 3.10+ |
| **Database** | SQLAlchemy, SQLite |
| **Vector Store** | Chroma |
| **LLM** | ollama |
| **Testing** | Pytest |
| **Infrastructure** | Docker, Docker Compose |
| **API Integrations** |Jira, Trello |

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+
- Git
- Docker (optional)

### Local Setup

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd ai_meeting_nodes
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your API keys (optional - system works without them).

5. **Start the server**
   ```bash
   uvicorn backend.app:app --reload
   ```

6. **Access the API**
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

### Docker Setup

```bash
docker-compose up --build
```

Access at `http://localhost:8000`

---

## 📂 Project Structure

```
ai_meeting_nodes/
├── backend/
│   ├── agents/              # AI agents (Decision, Task, Risk, Topic, Reasoner)
│   ├── api/                 # API routes
│   ├── core/                # Orchestrator, pipeline, workflow
│   ├── database/            # Models, ORM, vector DB
│   ├── input_layer/         # Audio/transcript handling
│   ├── processing/          # Text cleaning, segmentation
│   ├── rag/                 # Embeddings, retrieval, vector store
│   ├── task_engine/         # Task validation & structuring
│   ├── integrations/        # GitHub, Jira, Trello
│   ├── utils/               # Logger, helpers, constants
│   ├── app.py               # FastAPI app
│   └── config.py            # Configuration
├── data/embeddings/chroma/  # Vector database storage
├── scripts/                 # Helper scripts
├── tests/                   # Test suite
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 📊 Output Deliverables

Once a meeting is processed, the system generates:

1. **Structured Tasks**
   ```json
   {
     "task_id": "task_001",
     "title": "Implement authentication module",
     "description": "Add JWT-based auth to API",
     "priority": "High",
     "assignee": "john@example.com",
     "due_date": "2024-04-15"
   }
   ```

2. **Risk Assessment**
   ```json
   {
     "risk_id": "risk_001",
     "description": "Q2 deadline is aggressive",
     "severity": "Medium",
     "mitigation": "Consider hiring contractor"
   }
   ```

3. **Decision Log**
   ```json
   {
     "decision_id": "dec_001",
     "statement": "Migrate to microservices",
     "rationale": "Improve scalability",
     "context": "Discussed in Q1 planning"
   }
   ```

---

## ⚙️ Configuration

Create `.env` in project root:

```env
# Application
APP_ENV=dev
LOG_LEVEL=INFO

# Database
DATABASE_URL=sqlite:///./agentic_meeting_ai.db

# Vector Store
CHROMA_PERSIST_DIR=./data/embeddings/chroma
RAG_COLLECTION=meeting_ai

# LLM Provider
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Integrations
GITHUB_TOKEN=ghp_...
GITHUB_REPO=owner/repo

JIRA_BASE_URL=https://domain.atlassian.net
JIRA_EMAIL=user@example.com
JIRA_API_TOKEN=...
JIRA_PROJECT_KEY=PROJ

TRELLO_KEY=...
TRELLO_TOKEN=...
```

---

## 🧪 Testing

```bash
pytest -v                    # Run all tests
pytest tests/test_agents.py  # Test agents
pytest tests/test_pipeline.py # Test pipeline
pytest --cov                 # Coverage report
```

---

## 🎯 Key Features

- **Multi-Agent Processing** - 5 specialized agents analyze different aspects
- **RAG-Powered** - Semantic understanding with vector embeddings
- **Production-Ready** - Async/await, proper logging, error handling
- **Works Offline** - Runs without external API keys for testing
- **Docker Support** - Full containerization provided

---

## 📈 Performance

- **Processing**: ~1-2 seconds per minute of audio (with LLM)
- **Storage**: SQLite (upgradable to PostgreSQL)
- **Concurrency**: Handled via FastAPI async
- **Scaling**: Ready for horizontal scaling

---




