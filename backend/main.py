from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import Settings


def create_app() -> FastAPI:
    settings = Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        import asyncio
        from datetime import datetime, timezone

        from database import engine, Base, async_session
        import db_models  # noqa: F401
        from db_models.scrape_task import ScrapeTask
        from db_models.company import Company
        from sqlalchemy import select, func

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        if settings.app_mode == "demo":
            async with async_session() as session:
                count_result = await session.execute(
                    select(func.count(Company.id))
                )
                count = count_result.scalar() or 0

                if count == 0:
                    from demo.demo_seeder import seed_demo
                    from tasks.processing import process_and_save
                    from database_sync import get_sync_session

                    task = ScrapeTask(
                        source="demo-seed",
                        query="auto",
                        location="auto",
                        mode="demo",
                        status="running",
                        limit=500,
                        started_at=datetime.now(timezone.utc),
                    )
                    session.add(task)
                    await session.commit()
                    await session.refresh(task)
                    task_id = task.id

                    raw_dicts = seed_demo(count=500)
                    sync_session = get_sync_session()
                    scraped, cleaned, deduped, _ = await asyncio.to_thread(
                        process_and_save, raw_dicts, task_id, sync_session
                    )
                    sync_session.close()

                    task.total_scraped = scraped
                    task.total_cleaned = cleaned
                    task.total_deduped = deduped
                    task.status = "completed"
                    task.completed_at = datetime.now(timezone.utc)
                    await session.commit()

        yield
        await engine.dispose()

    app = FastAPI(
        title="Lead Gen Scraper API",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from api.routes.tasks import router as tasks_router
    from api.routes.results import router as results_router
    from api.routes.export import router as export_router
    from api.routes.sources import router as sources_router
    from api.routes.pipeline import router as pipeline_router
    from api.routes.demo import router as demo_router
    from api.routes.mode import router as mode_router
    from api.ws import router as ws_router

    app.include_router(tasks_router, prefix="/api/v1/tasks")
    app.include_router(results_router, prefix="/api/v1/results")
    app.include_router(export_router, prefix="/api/v1/export")
    app.include_router(sources_router, prefix="/api/v1/sources")
    app.include_router(pipeline_router, prefix="/api/v1/pipeline")
    app.include_router(demo_router, prefix="/api/v1/demo")
    app.include_router(mode_router, prefix="/api/v1/mode")
    app.include_router(ws_router)

    return app


app = create_app()
