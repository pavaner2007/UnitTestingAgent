from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AutoQA Agent"
    environment: str = "development"
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/autoqa_agent"
    workspace_dir: str = "../repositories"
    reports_dir: str = "../reports"
    log_level: str = "INFO"
    groq_api_key: str | None = None
    ollama_base_url: str = "http://localhost:11434"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def workspace_path(self) -> Path:
        return Path(self.workspace_dir).resolve()

    @property
    def reports_path(self) -> Path:
        return Path(self.reports_dir).resolve()


settings = Settings()
