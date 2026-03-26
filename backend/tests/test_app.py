import pytest
from httpx import ASGITransport, AsyncClient

from main import create_app


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
async def client(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


class TestApp:
    @pytest.mark.asyncio
    async def test_app_creates(self, app):
        assert app.title == "Lead Gen Scraper API"

    @pytest.mark.asyncio
    async def test_docs_endpoint(self, client):
        resp = await client.get("/docs")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_cors_headers(self, client):
        resp = await client.options(
            "/api/v1/tasks",
            headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"},
        )
        assert "access-control-allow-origin" in resp.headers
