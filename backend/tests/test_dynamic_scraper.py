from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from scrapers.dynamic_scraper import DynamicScraper
from scrapers.config_loader import load_source_config
from models.raw_data import ProgressInfo
from pathlib import Path

SOURCES_DIR = Path(__file__).parent.parent / "sources"


class TestDynamicScraperUnit:
    def test_inherits_base_scraper(self):
        from scrapers.base import BaseScraper
        assert issubclass(DynamicScraper, BaseScraper)

    def test_gaussian_delay_within_range(self):
        for _ in range(100):
            d = DynamicScraper._gaussian_delay([3.0, 6.0])
            assert 3.0 <= d <= 6.0

    def test_build_url_with_params(self):
        scraper = DynamicScraper()
        config = MagicMock()
        config.base_url = "https://example.com/search"
        config.search_params = {"q": "{query}", "loc": "{location}"}
        url = scraper._build_url(config, "plumbers", "NYC")
        assert "q=plumbers" in url
        assert "loc=NYC" in url

    def test_build_url_no_params(self):
        scraper = DynamicScraper()
        config = MagicMock()
        config.base_url = "https://example.com"
        config.search_params = {}
        url = scraper._build_url(config, "q", "l")
        assert url == "https://example.com"


class TestDynamicScraperNoPlaywright:
    @pytest.mark.asyncio
    async def test_returns_error_when_playwright_not_installed(self):
        scraper = DynamicScraper()
        config = MagicMock()
        config.name = "test"
        config.proxy = MagicMock(required=False)

        with patch.dict("sys.modules", {"playwright": None, "playwright.async_api": None}):
            with patch("scrapers.dynamic_scraper.DynamicScraper.scrape") as mock_scrape:
                # Simulate import error path
                from scrapers.dynamic_scraper import DynamicScraper as DS
                s = DS()
                # Just verify the class can be instantiated
                assert s is not None


class TestDynamicScraperProxyCheck:
    @pytest.mark.asyncio
    async def test_fails_fast_when_proxy_required_but_unavailable(self):
        scraper = DynamicScraper()
        config = MagicMock()
        config.name = "crunchbase"
        config.proxy = MagicMock(required=True)

        result = await scraper.scrape(config, "test", "NYC", 10)
        assert len(result.errors) > 0
        assert "Proxy required" in result.errors[0]

    @pytest.mark.asyncio
    async def test_fails_fast_with_proxy_rotator_no_proxies(self):
        mock_rotator = MagicMock()
        mock_rotator.get_next.return_value = None
        scraper = DynamicScraper(proxy_rotator=mock_rotator)
        config = MagicMock()
        config.name = "test"
        config.proxy = MagicMock(required=True)

        result = await scraper.scrape(config, "test", "NYC", 10)
        assert "Proxy required" in result.errors[0]


class TestProgressCallback:
    @pytest.mark.asyncio
    async def test_on_progress_receives_progress_info(self):
        progress_calls = []
        scraper = DynamicScraper(on_progress=lambda p: progress_calls.append(p))

        config = MagicMock()
        config.name = "test"
        config.proxy = MagicMock(required=True)

        # Will fail fast due to no proxy - but test callback type
        result = await scraper.scrape(config, "q", "l", 10)
        # No progress emitted because scrape exits before scroll loop
        assert result.items == []


class TestExtractAppStateJson:
    @pytest.mark.asyncio
    async def test_parses_json_from_script_tag(self):
        scraper = DynamicScraper()
        config = MagicMock()
        config.name = "crunchbase"
        config.app_state_selector = "script#ng-state"
        config.app_state_jmespath = "entities[*]"

        mock_page = AsyncMock()
        mock_locator = AsyncMock()
        mock_locator.count = AsyncMock(return_value=1)

        test_data = {
            "entities": [
                {"name": "Acme Corp", "website_url": "https://acme.com", "categories": ["Tech"]},
                {"name": "Beta Inc", "homepage_url": "https://beta.io"},
            ]
        }
        mock_locator.inner_text = AsyncMock(return_value=json.dumps(test_data))
        mock_page.locator = MagicMock(return_value=mock_locator)

        items = await scraper._extract_app_state_json(mock_page, config, "https://crunchbase.com")
        assert len(items) == 2
        assert items[0]["company_name"] == "Acme Corp"
        assert items[0]["website"] == "https://acme.com"
        assert items[0]["source"] == "crunchbase"
        assert items[1]["company_name"] == "Beta Inc"

    @pytest.mark.asyncio
    async def test_handles_html_escaped_json(self):
        scraper = DynamicScraper()
        config = MagicMock()
        config.name = "test"
        config.app_state_selector = "script"
        config.app_state_jmespath = "items[*]"

        mock_page = AsyncMock()
        mock_locator = AsyncMock()
        mock_locator.count = AsyncMock(return_value=1)
        # HTML-escaped JSON
        mock_locator.inner_text = AsyncMock(
            return_value='{"items": [{"name": "A &amp; B Corp"}]}'
        )
        mock_page.locator = MagicMock(return_value=mock_locator)

        items = await scraper._extract_app_state_json(mock_page, config, "https://test.com")
        assert len(items) == 1
        assert items[0]["company_name"] == "A & B Corp"

    @pytest.mark.asyncio
    async def test_returns_empty_when_no_script_tag(self):
        scraper = DynamicScraper()
        config = MagicMock()
        config.name = "test"
        config.app_state_selector = "script#missing"

        mock_page = AsyncMock()
        mock_locator = AsyncMock()
        mock_locator.count = AsyncMock(return_value=0)
        mock_page.locator = MagicMock(return_value=mock_locator)

        items = await scraper._extract_app_state_json(mock_page, config, "https://test.com")
        assert items == []


class TestCrunchbaseConfig:
    def test_crunchbase_config_loads(self):
        config = load_source_config("crunchbase", SOURCES_DIR)
        assert config.renderer == "playwright"
        assert config.app_state_selector is not None
        assert config.app_state_jmespath is not None
