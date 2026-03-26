from __future__ import annotations

import functools
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from config import Settings
from database import async_session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    session = async_session()
    try:
        yield session
    finally:
        await session.close()


@functools.lru_cache
def _get_settings() -> Settings:
    return Settings()


async def get_settings() -> Settings:
    return _get_settings()


async def get_current_mode() -> str:
    settings = _get_settings()
    return settings.app_mode
