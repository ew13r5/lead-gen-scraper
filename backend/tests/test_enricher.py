import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from pipeline.enricher import Enricher, _is_safe_url


def rec(**kw):
    return {"company_name": "Test", "_pipeline_id": "id-1", "website": "https://example.com", **kw}


class TestUrlSafety:
    def test_private_ip_rejected(self):
        assert _is_safe_url("http://192.168.1.1/page") is False

    def test_localhost_rejected(self):
        assert _is_safe_url("http://localhost/page") is False

    def test_non_http_rejected(self):
        assert _is_safe_url("ftp://example.com") is False

    def test_valid_url_accepted(self):
        assert _is_safe_url("https://example.com") is True


class TestEnricher:
    def test_website_alive_true(self):
        enricher = Enricher()
        data = [rec()]
        with patch("pipeline.enricher.httpx.AsyncClient") as MockClient:
            mock = AsyncMock()
            mock.head = AsyncMock(return_value=httpx.Response(200))
            mock.get = AsyncMock(return_value=httpx.Response(200, text="<html></html>"))
            mock.__aenter__ = AsyncMock(return_value=mock)
            mock.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock
            result, _ = enricher.run(data)
            assert result[0].get("website_alive") is True

    def test_website_alive_false_404(self):
        enricher = Enricher()
        data = [rec()]
        with patch("pipeline.enricher.httpx.AsyncClient") as MockClient:
            mock = AsyncMock()
            mock.head = AsyncMock(return_value=httpx.Response(404))
            mock.get = AsyncMock(return_value=httpx.Response(404))
            mock.__aenter__ = AsyncMock(return_value=mock)
            mock.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock
            result, _ = enricher.run(data)
            assert result[0].get("website_alive") is False

    def test_records_never_removed(self):
        enricher = Enricher()
        data = [rec(), rec(_pipeline_id="id-2")]
        with patch("pipeline.enricher.httpx.AsyncClient") as MockClient:
            mock = AsyncMock()
            mock.head = AsyncMock(return_value=httpx.Response(200))
            mock.get = AsyncMock(return_value=httpx.Response(200, text="<html></html>"))
            mock.__aenter__ = AsyncMock(return_value=mock)
            mock.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock
            _, sr = enricher.run(data)
            assert sr.count_in == sr.count_out

    def test_no_website_skipped(self):
        enricher = Enricher()
        data = [{"company_name": "Test", "_pipeline_id": "id-1"}]
        result, sr = enricher.run(data)
        assert "website_alive" not in result[0]

    def test_stats_tracked(self):
        enricher = Enricher()
        data = [rec()]
        with patch("pipeline.enricher.httpx.AsyncClient") as MockClient:
            mock = AsyncMock()
            mock.head = AsyncMock(return_value=httpx.Response(200))
            mock.get = AsyncMock(return_value=httpx.Response(200, text="<html></html>"))
            mock.__aenter__ = AsyncMock(return_value=mock)
            mock.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock
            _, sr = enricher.run(data)
            assert "websites_checked" in sr.details
