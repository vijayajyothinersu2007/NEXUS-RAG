"""Centralized application settings loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic import SecretStr
from pydantic.aliases import AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Runtime configuration for NexusRAG."""

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="NexusRAG")
    app_env: str = Field(default="development")
    log_level: str = Field(default="INFO")

    data_dir: Path = Field(default=PROJECT_ROOT / "data")
    max_upload_mb: int = Field(default=25)

    gemini_api_key: SecretStr = Field(
        default=SecretStr(""),
        validation_alias=AliasChoices("GEMINI_API_KEY", "gemini_api_key"),
        repr=False,
    )
    llm_model: str = Field(default="gemini-3.6-flash")
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")

    allowed_extensions: tuple[str, ...] = (
        ".pdf",
        ".docx",
        ".txt",
        ".csv",
        ".xlsx",
    )

    @property
    def documents_dir(self) -> Path:
        return self.data_dir / "documents"

    @property
    def processed_dir(self) -> Path:
        return self.data_dir / "processed"

    @property
    def registry_path(self) -> Path:
        return self.processed_dir / "registry.json"

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024

    def ensure_directories(self) -> None:
        self.documents_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        (PROJECT_ROOT / "vectorstore").mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    if not settings.data_dir.is_absolute():
        settings.data_dir = PROJECT_ROOT / settings.data_dir
    settings.ensure_directories()
    return settings
