from __future__ import annotations

from sqlalchemy import text

from database_sync import get_sync_url, get_sync_session


class TestGetSyncUrl:
    def test_converts_asyncpg_to_psycopg2(self):
        assert get_sync_url("postgresql+asyncpg://user:pw@host/db") == "postgresql+psycopg2://user:pw@host/db"

    def test_converts_aiosqlite_to_sqlite(self):
        assert get_sync_url("sqlite+aiosqlite:///./test.db") == "sqlite:///./test.db"

    def test_passthrough_unknown(self):
        assert get_sync_url("mysql://host/db") == "mysql://host/db"


class TestGetSyncSession:
    def test_creates_working_session(self):
        from unittest.mock import patch
        with patch("database_sync.Settings") as MockSettings:
            MockSettings.return_value.database_url = "sqlite+aiosqlite:///./test_sync.db"
            session = get_sync_session()
            result = session.execute(text("SELECT 1"))
            assert result.scalar() == 1
            session.close()


class TestScrapeTaskEnrich:
    def test_has_enrich_column(self):
        from db_models.scrape_task import ScrapeTask
        assert "enrich" in ScrapeTask.__table__.columns
        col = ScrapeTask.__table__.columns["enrich"]
        assert col.default.arg is False


class TestSettingsSourcesDir:
    def test_has_sources_dir(self):
        from config import Settings
        s = Settings(_env_file=None)
        assert hasattr(s, "sources_dir")
        assert s.sources_dir == "./sources"
