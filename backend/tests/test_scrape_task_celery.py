from __future__ import annotations

import uuid
from unittest.mock import patch, MagicMock

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from database import Base
import db_models  # noqa: F401
from db_models.scrape_task import ScrapeTask
from db_models.company import Company


def _setup(mode="demo", limit=10):
    engine = create_engine("sqlite://", echo=False)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    session = factory()
    task_id = str(uuid.uuid4())
    task = ScrapeTask(
        id=task_id,
        source="yellowpages",
        query="plumbers",
        location="NYC",
        limit=limit,
        mode=mode,
        status="pending",
    )
    session.add(task)
    session.commit()
    session.close()
    return factory, task_id


class TestRunScrape:
    @patch("tasks.scrape_task.get_sync_session")
    def test_demo_mode_saves_data(self, mock_get_session):
        factory, task_id = _setup(mode="demo", limit=10)
        mock_get_session.return_value = factory()

        from tasks.scrape_task import run_scrape
        run_scrape(task_id)

        session = factory()
        task = session.get(ScrapeTask, task_id)
        assert task.status == "completed"
        assert task.total_scraped > 0
        assert task.completed_at is not None

        companies = session.execute(select(Company)).scalars().all()
        assert len(companies) > 0
        session.close()

    @patch("tasks.scrape_task.get_sync_session")
    def test_sets_failed_on_exception(self, mock_get_session):
        factory, task_id = _setup(mode="demo", limit=5)
        mock_get_session.return_value = factory()

        with patch("tasks.scrape_task.process_and_save", side_effect=RuntimeError("boom")):
            from tasks.scrape_task import run_scrape
            run_scrape(task_id)

        session = factory()
        task = session.get(ScrapeTask, task_id)
        assert task.status == "failed"
        assert "boom" in task.error_message
        session.close()

    @patch("tasks.scrape_task.get_sync_session")
    def test_handles_null_limit(self, mock_get_session):
        factory, task_id = _setup(mode="demo", limit=None)
        mock_get_session.return_value = factory()

        with patch("demo.demo_seeder.seed_demo", return_value=[
            {"company_name": "Test Co", "phone": "555-1234", "source": "demo",
             "source_url": "http://demo.com", "scraped_at": "2026-01-01T00:00:00"}
        ]) as mock_seed:
            from tasks.scrape_task import run_scrape
            run_scrape(task_id)
            mock_seed.assert_called_once_with(count=200)
