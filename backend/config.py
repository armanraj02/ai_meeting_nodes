from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment and `.env`."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "dev"
    log_level: str = "INFO"

    database_url: str = "sqlite:///./agentic_meeting_ai.db"

    chroma_persist_dir: str = "./data/embeddings/chroma"
    rag_collection: str = "meeting_ai"

    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    github_token: str | None = None
    github_repo: str | None = None

    jira_base_url: str | None = None
    jira_email: str | None = None
    jira_api_token: str | None = None
    jira_project_key: str | None = None

    trello_key: str | None = None
    trello_token: str | None = None
    trello_list_id: str | None = None


def get_settings() -> Settings:
    return Settings()

