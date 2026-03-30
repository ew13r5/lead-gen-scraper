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


def _make_publisher(settings: Settings):
    """Create RedisPublisher, returns None if Redis unavailable."""
    try:
        from api.pubsub import RedisPublisher
        return RedisPublisher(settings.redis_url)
    except Exception:
        return None


@celery_app.task(bind=True)
def run_scrape(self, task_id: str) -> None:
    """Execute scrape + pipeline + save for a task."""
    settings = Settings()
    publisher = _make_publisher(settings)
    channel = f"task:{task_id}:events"
    session = get_sync_session()

    def publish(msg: dict) -> None:
        if publisher:
            try:
                publisher.publish(channel, msg)
            except Exception:
                pass

    try:
        task = session.get(ScrapeTask, task_id)
        if not task:
            logger.error("Task %s not found", task_id)
            return

        task.status = "running"
        task.started_at = datetime.utcnow()
        session.commit()

        def on_progress(info) -> None:
            publish({
                "type": "progress",
                "pages_processed": info.pages_processed,
                "pages_total": info.pages_total,
                "items_found": info.items_found,
                "errors": info.errors,
                "stage": "scraping",
            })

        if task.mode == "demo":
            from demo.demo_seeder import seed_demo
            raw_dicts = seed_demo(count=task.limit or 200)
            publish({"type": "progress", "stage": "scraping", "pages_processed": 1, "pages_total": 1, "items_found": len(raw_dicts), "errors": 0})
        else:
            from asgiref.sync import async_to_sync
            from scrapers.source_router import SourceRouter

            router = SourceRouter(sources_dir=Path(settings.sources_dir))
            result = async_to_sync(router.scrape)(
                task.source, task.query, task.location, task.limit or 200,
                on_progress=on_progress,
            )
            raw_dicts = result.items

        publish({"type": "progress", "stage": "cleaning", "pages_processed": 0, "pages_total": None, "items_found": len(raw_dicts), "errors": 0})

        scraped, cleaned, deduped, _ = process_and_save(
            raw_dicts, task_id, session, enrich=task.enrich
        )

        publish({"type": "results_update", "task_id": task_id, "new_count": deduped, "total": deduped})

        task.total_scraped = scraped
        task.total_cleaned = cleaned
        task.total_deduped = deduped
        task.status = "completed"
        task.completed_at = datetime.utcnow()
        session.commit()

        publish({
            "type": "task_completed",
            "task_id": task_id,
            "total_scraped": scraped,
            "total_cleaned": cleaned,
            "total_deduped": deduped,
        })

    except Exception as e:
        logger.exception("Task %s failed", task_id)
        publish({"type": "task_failed", "task_id": task_id, "error": str(e)})
        try:
            task = session.get(ScrapeTask, task_id)
            if task:
                task.status = "failed"
                task.error_message = str(e)
                task.completed_at = datetime.utcnow()
                session.commit()
        except Exception:
            logger.exception("Failed to update task status")
    finally:
        session.close()
