from __future__ import annotations

import uuid

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from database import Base
import db_models  # noqa: F401
from db_models.company import Company
from db_models.scrape_task import ScrapeTask
from db_models.pipeline_stat import PipelineStat
from tasks.processing import process_and_save


def _make_session() -> Session:
    engine = create_engine("sqlite://", echo=False)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def _make_task(session: Session) -> ScrapeTask:
    task = ScrapeTask(
        id=str(uuid.uuid4()),
        source="demo",
        query="test",
        location="test",
        mode="demo",
        status="running",
    )
    session.add(task)
    session.commit()
    return task


def _sample_dicts(n: int = 5) -> list[dict]:
    return [
        {
            "company_name": f"Company {i}",
            "phone": f"+1-555-000-{i:04d}",
            "email": f"info{i}@company{i}.com",
            "website": f"https://company{i}.com",
            "address": f"{i} Main St",
            "city": "New York",
            "state": "NY",
            "category": "Test",
            "rating": "4.5",
            "review_count": 10,
            "source": "demo",
            "source_url": f"https://demo.com/{i}",
            "scraped_at": "2026-01-01T00:00:00",
        }
        for i in range(n)
    ]


class TestProcessAndSave:
    def test_inserts_company_records_with_task_id(self):
        session = _make_session()
        task = _make_task(session)
        process_and_save(_sample_dicts(3), task.id, session)

        companies = session.execute(select(Company)).scalars().all()
        assert len(companies) >= 1
        for c in companies:
            assert c.task_id == task.id

    def test_creates_pipeline_stat_records(self):
        session = _make_session()
        task = _make_task(session)
        process_and_save(_sample_dicts(5), task.id, session)

        stats = session.execute(select(PipelineStat)).scalars().all()
        assert len(stats) >= 3  # HTMLCleaner, FieldValidator, Deduplicator
        for stat in stats:
            assert stat.task_id == task.id
            assert stat.count_in > 0

    def test_maps_pipeline_fields(self):
        session = _make_session()
        task = _make_task(session)
        process_and_save(_sample_dicts(1), task.id, session)

        company = session.execute(select(Company)).scalar_one()
        assert company.pipeline_id is not None
        assert isinstance(company.rating, float)
        assert company.rating == 4.5

    def test_returns_correct_counts(self):
        session = _make_session()
        task = _make_task(session)
        scraped, cleaned, deduped, stages = process_and_save(
            _sample_dicts(5), task.id, session
        )
        assert scraped == 5
        assert cleaned <= scraped
        assert deduped <= cleaned
        assert len(stages) >= 3
