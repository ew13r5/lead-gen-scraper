import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session, sessionmaker

from database import Base
from db_models import ScrapeTask, Company, PipelineStat, ExportLog
from config import Settings


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


class TestScrapeTask:
    def test_creates_with_defaults(self, db_session):
        task = ScrapeTask(source="yellowpages", query="plumbers", location="NYC")
        db_session.add(task)
        db_session.commit()
        assert task.id is not None
        assert task.status == "pending"
        assert task.mode == "demo"
        assert task.total_scraped == 0

    def test_status_default_pending(self, db_session):
        task = ScrapeTask(source="yelp", query="test", location="NY")
        db_session.add(task)
        db_session.commit()
        assert task.status == "pending"


class TestCompany:
    def test_creates_with_all_fields(self, db_session):
        task = ScrapeTask(source="yp", query="q", location="l")
        db_session.add(task)
        db_session.commit()

        company = Company(
            company_name="Acme Corp",
            phone="+12125551234",
            email="info@acme.com",
            website="https://acme.com",
            city="New York",
            state="NY",
            source="yellowpages",
            task_id=task.id,
        )
        db_session.add(company)
        db_session.commit()
        assert company.id is not None
        assert company.email_validated is False
        assert company.needs_review is False

    def test_is_duplicate_of_fk(self, db_session):
        c1 = Company(company_name="Primary")
        db_session.add(c1)
        db_session.commit()
        c2 = Company(company_name="Duplicate", is_duplicate_of=c1.id)
        db_session.add(c2)
        db_session.commit()
        assert c2.is_duplicate_of == c1.id


class TestPipelineStat:
    def test_links_to_task(self, db_session):
        task = ScrapeTask(source="test", query="q", location="l")
        db_session.add(task)
        db_session.commit()
        stat = PipelineStat(task_id=task.id, stage="html_cleaner", count_in=100, count_out=100)
        db_session.add(stat)
        db_session.commit()
        assert stat.task_id == task.id


class TestExportLog:
    def test_links_to_task(self, db_session):
        task = ScrapeTask(source="test", query="q", location="l")
        db_session.add(task)
        db_session.commit()
        log = ExportLog(task_id=task.id, format="csv", rows_exported=50)
        db_session.add(log)
        db_session.commit()
        assert log.task_id == task.id


class TestSettings:
    def test_defaults(self):
        s = Settings(_env_file=None, database_url="sqlite:///test.db")
        assert s.redis_url == "redis://localhost:6379/0"
        assert s.app_mode == "demo"
