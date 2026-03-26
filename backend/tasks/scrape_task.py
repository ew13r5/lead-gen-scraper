from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

from tasks.celery_app import celery_app
from config import Settings
from database_sync import get_sync_session
from db_models.scrape_task import ScrapeTask
from tasks.processing import process_and_save

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def run_scrape(self, task_id: str) -> None:
    """Execute scrape + pipeline + save for a task."""
    session = get_sync_session()
    try:
        task = session.get(ScrapeTask, task_id)
        if not task:
            logger.error("Task %s not found", task_id)
            return

        task.status = "running"
        task.started_at = datetime.now(timezone.utc)
        session.commit()

        if task.mode == "demo":
            from demo.demo_seeder import seed_demo
            raw_dicts = seed_demo(count=task.limit or 200)
        else:
            from asgiref.sync import async_to_sync
            from scrapers.source_router import SourceRouter

            settings = Settings()
            router = SourceRouter(sources_dir=Path(settings.sources_dir))
            result = async_to_sync(router.scrape)(
                task.source, task.query, task.location, task.limit or 200
            )
            raw_dicts = result.items

        scraped, cleaned, deduped, _ = process_and_save(
            raw_dicts, task_id, session, enrich=task.enrich
        )

        task.total_scraped = scraped
        task.total_cleaned = cleaned
        task.total_deduped = deduped
        task.status = "completed"
        task.completed_at = datetime.now(timezone.utc)
        session.commit()

    except Exception as e:
        logger.exception("Task %s failed", task_id)
        try:
            task = session.get(ScrapeTask, task_id)
            if task:
                task.status = "failed"
                task.error_message = str(e)
                task.completed_at = datetime.now(timezone.utc)
                session.commit()
        except Exception:
            logger.exception("Failed to update task status")
    finally:
        session.close()
