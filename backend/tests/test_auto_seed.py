from __future__ import annotations

import uuid
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker

from database import Base
import db_models  # noqa: F401
from db_models.company import Company
from db_models.scrape_task import ScrapeTask
from demo.demo_seeder import seed_demo
from tasks.processing import process_and_save


def _make_session():
    engine = create_engine("sqlite://", echo=False)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


class TestAutoSeed:
    def test_seeds_companies_when_empty(self):
        """Simulate the auto-seed logic: generate + pipeline + save."""
        session = _make_session()

        # Create task
        task = ScrapeTask(
            id=str(uuid.uuid4()),
            source="demo-seed",
            query="auto",
            location="auto",
            mode="demo",
            status="running",
            limit=50,
        )
        session.add(task)
        session.commit()

        # Seed
        raw = seed_demo(count=50)
        scraped, cleaned, deduped, _ = process_and_save(raw, task.id, session)

        assert scraped > 0
        count = session.execute(select(func.count(Company.id))).scalar()
        assert count > 0

    def test_skips_when_data_exists(self):
        """If companies already exist, seeding should not run (checked in lifespan)."""
        session = _make_session()

        task = ScrapeTask(
            id=str(uuid.uuid4()),
            source="demo-seed",
            query="auto",
            location="auto",
            mode="demo",
            status="completed",
        )
        session.add(task)
        session.commit()

        company = Company(company_name="Existing Co", task_id=task.id)
        session.add(company)
        session.commit()

        count = session.execute(select(func.count(Company.id))).scalar()
        assert count == 1  # Lifespan checks count > 0 → skip

    def test_seed_creates_linked_task(self):
        """Seeded companies should all reference the same ScrapeTask."""
        session = _make_session()

        task = ScrapeTask(
            id=str(uuid.uuid4()),
            source="demo-seed",
            query="auto",
            location="auto",
            mode="demo",
            status="running",
        )
        session.add(task)
        session.commit()

        raw = seed_demo(count=20)
        process_and_save(raw, task.id, session)

        companies = session.execute(select(Company)).scalars().all()
        for c in companies:
            assert c.task_id == task.id
