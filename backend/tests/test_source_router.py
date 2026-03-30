import pytest
from unittest.mock import AsyncMock, patch
from pathlib import Path

from scrapers.source_router import SourceRouter
from scrapers.config_loader import SourceConfig

VALID_YAML = """
name: test_source
base_url: "https://example.com"
renderer: static
search_params:
  q: "{query}"
pagination:
  type: url_param
  param: page
  start: 1
  max_pages: 1
listing_selector: "div.item"
selectors:
  name: "h3::text"
rate_limit:
  delay_range: [0.01, 0.02]
  concurrent: 1
  max_retries: 1
proxy:
  required: false
"""


@pytest.fixture
def sources_dir(tmp_path):
    (tmp_path / "test_source.yaml").write_text(VALID_YAML)
    (tmp_path / "second.yaml").write_text(VALID_YAML.replace("name: test_source", "name: second"))
    return tmp_path


class TestSourceRouter:
    def test_list_sources(self, sources_dir):
        router = SourceRouter(sources_dir)
        sources = router.list_sources()
        assert set(sources) == {"test_source", "second"}

    def test_get_config(self, sources_dir):
        router = SourceRouter(sources_dir)
        config = router.get_config("test_source")
        assert isinstance(config, SourceConfig)
        assert config.name == "test_source"

    def test_get_config_unknown_raises(self, sources_dir):
        router = SourceRouter(sources_dir)
        with pytest.raises(FileNotFoundError):
            router.get_config("nonexistent")

    @pytest.mark.asyncio
    async def test_scrape_routes_to_static(self, sources_dir):
        router = SourceRouter(sources_dir)
        with patch("scrapers.source_router.StaticScraper") as MockScraper:
            mock_instance = MockScraper.return_value
            mock_instance.scrape = AsyncMock(return_value=AsyncMock(
                items=[], pages_scraped=0, pages_skipped=0, errors=[],
                source="test", total_time_seconds=0.1
            ))
            await router.scrape("test_source", "q", "l", 10)
            MockScraper.assert_called_once()
            mock_instance.scrape.assert_called_once()

    @pytest.mark.asyncio
    async def test_playwright_dispatches_to_dynamic_scraper(self, tmp_path):
        pw_yaml = VALID_YAML.replace("renderer: static", "renderer: playwright").replace("name: test_source", "name: pw")
        (tmp_path / "pw.yaml").write_text(pw_yaml)
        router = SourceRouter(tmp_path)
        # DynamicScraper will return an error (no playwright installed)
        # but it should NOT raise NotImplementedError
        result = await router.scrape("pw", "q", "l", 10)
        assert result is not None
        assert result.source == "pw"
