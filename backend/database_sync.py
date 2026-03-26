from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from config import Settings


def get_sync_url(async_url: str) -> str:
    """Convert async database URL to sync equivalent."""
    if "+asyncpg" in async_url:
        return async_url.replace("+asyncpg", "+psycopg2")
    if "+aiosqlite" in async_url:
        return async_url.replace("+aiosqlite", "")
    return async_url


def get_sync_session() -> Session:
    """Create a sync session for Celery tasks."""
    settings = Settings()
    sync_url = get_sync_url(settings.database_url)
    engine = create_engine(sync_url)
    factory = sessionmaker(bind=engine)
    return factory()
