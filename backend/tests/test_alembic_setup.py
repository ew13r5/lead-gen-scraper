from __future__ import annotations

import pytest
from database import Base
import db_models  # noqa: F401


class TestAlembicMetadata:
    def test_target_metadata_has_all_tables(self):
        table_names = set(Base.metadata.tables.keys())
        assert "companies" in table_names
        assert "scrape_tasks" in table_names
        assert "pipeline_stats" in table_names
        assert "export_log" in table_names

    def test_metadata_has_at_least_4_tables(self):
        assert len(Base.metadata.tables) >= 4


class TestLifespanCreateAll:
    @pytest.mark.asyncio
    async def test_lifespan_creates_tables(self):
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import inspect

        engine = create_async_engine("sqlite+aiosqlite://", echo=False)

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with engine.connect() as conn:
            table_names = await conn.run_sync(
                lambda sync_conn: inspect(sync_conn).get_table_names()
            )

        assert "companies" in table_names
        assert "scrape_tasks" in table_names
        assert "pipeline_stats" in table_names
        assert "export_log" in table_names

        await engine.dispose()
