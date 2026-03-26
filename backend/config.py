from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str = "sqlite+aiosqlite:///./leadgen.db"
    redis_url: str = "redis://localhost:6379/0"
    app_mode: str = "demo"
    exports_dir: str = "./exports"
    sources_dir: str = "./sources"
    google_sheets_credentials: str | None = None
    cors_origins: list[str] = ["http://localhost:3000"]
