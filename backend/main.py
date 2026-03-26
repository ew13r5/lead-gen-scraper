from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import Settings


def create_app() -> FastAPI:
    settings = Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
        from database import engine
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

    app.include_router(tasks_router, prefix="/api/v1/tasks")
    app.include_router(results_router, prefix="/api/v1/results")
    app.include_router(export_router, prefix="/api/v1/export")
    app.include_router(sources_router, prefix="/api/v1/sources")
    app.include_router(pipeline_router, prefix="/api/v1/pipeline")
    app.include_router(demo_router, prefix="/api/v1/demo")
    app.include_router(mode_router, prefix="/api/v1/mode")

    return app


app = create_app()
