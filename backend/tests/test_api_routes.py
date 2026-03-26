import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base
from main import create_app
from api.deps import get_db


@pytest.fixture
def sync_engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def app(sync_engine):
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
    import aiosqlite

    async_engine = create_async_engine("sqlite+aiosqlite://", echo=False)

    # Create tables on async engine
    import asyncio

    async def setup():
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.get_event_loop().run_until_complete(setup()) if False else None

    _app = create_app()

    # Override get_db to use sync session wrapped for async compatibility
    SessionLocal = sessionmaker(bind=sync_engine)

    async def override_get_db():
        # For simple test, use sync session in async context via run_sync
        from sqlalchemy.ext.asyncio import AsyncSession

        class FakeAsyncSession:
            def __init__(self):
                self._session = SessionLocal()

            async def execute(self, stmt):
                return self._session.execute(stmt)

            def add(self, obj):
                self._session.add(obj)

            async def commit(self):
                self._session.commit()

            async def refresh(self, obj):
                self._session.refresh(obj)

            async def close(self):
                self._session.close()

        yield FakeAsyncSession()

    _app.dependency_overrides[get_db] = override_get_db
    return _app


@pytest.fixture
async def client(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


class TestTaskRoutes:
    @pytest.mark.asyncio
    async def test_create_task(self, client):
        resp = await client.post("/api/v1/tasks/", json={
            "source": "yellowpages", "query": "plumbers", "location": "NYC"
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "pending"
        assert data["source"] == "yellowpages"

    @pytest.mark.asyncio
    async def test_create_invalid_source(self, client):
        resp = await client.post("/api/v1/tasks/", json={
            "source": "invalid", "query": "q", "location": "l"
        })
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_list_tasks(self, client):
        await client.post("/api/v1/tasks/", json={"source": "yelp", "query": "q", "location": "l"})
        resp = await client.get("/api/v1/tasks/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1

    @pytest.mark.asyncio
    async def test_get_task(self, client):
        create_resp = await client.post("/api/v1/tasks/", json={"source": "bbb", "query": "q", "location": "l"})
        task_id = create_resp.json()["id"]
        resp = await client.get(f"/api/v1/tasks/{task_id}")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_get_task_404(self, client):
        resp = await client.get("/api/v1/tasks/nonexistent")
        assert resp.status_code == 404


class TestSourceRoutes:
    @pytest.mark.asyncio
    async def test_list_sources(self, client):
        resp = await client.get("/api/v1/sources/")
        assert resp.status_code == 200
        assert len(resp.json()) == 4

    @pytest.mark.asyncio
    async def test_validate_valid(self, client):
        resp = await client.post("/api/v1/sources/yellowpages/validate")
        assert resp.status_code == 200
        assert resp.json()["valid"] is True

    @pytest.mark.asyncio
    async def test_validate_invalid(self, client):
        resp = await client.post("/api/v1/sources/nonexistent/validate")
        assert resp.status_code == 404


class TestModeRoutes:
    @pytest.mark.asyncio
    async def test_get_mode(self, client):
        resp = await client.get("/api/v1/mode/")
        assert resp.status_code == 200
        assert "mode" in resp.json()

    @pytest.mark.asyncio
    async def test_set_mode(self, client):
        resp = await client.put("/api/v1/mode/", json={"mode": "live"})
        assert resp.status_code == 200
        assert resp.json()["mode"] == "live"

    @pytest.mark.asyncio
    async def test_set_invalid_mode(self, client):
        resp = await client.put("/api/v1/mode/", json={"mode": "invalid"})
        assert resp.status_code == 422
