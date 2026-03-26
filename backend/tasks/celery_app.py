from celery import Celery
from config import Settings

settings = Settings()

celery_app = Celery(
    "lead_gen_scraper",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    result_expires=86400,
    timezone="UTC",
    include=["tasks.scrape_task"],
)
