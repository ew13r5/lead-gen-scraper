from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db
from config import Settings

router = APIRouter(tags=["health"])


@router.get("/")
async def health_check(db: AsyncSession = Depends(get_db)):
    settings = Settings()
    postgres_ok = False
    redis_ok = False

    try:
        await db.execute(text("SELECT 1"))
        postgres_ok = True
    except Exception:
        pass

    try:
        import redis.asyncio as aioredis
        r = aioredis.from_url(settings.redis_url)
        await r.ping()
        await r.close()
        redis_ok = True
    except Exception:
        pass

    status = "healthy" if postgres_ok and redis_ok else "unhealthy"
    return {"status": status, "postgres": postgres_ok, "redis": redis_ok}
