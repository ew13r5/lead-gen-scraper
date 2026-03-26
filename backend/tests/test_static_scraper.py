import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from cache.html_cache import HtmlCache
from models.raw_data import ScrapeResult
from scrapers.config_loader import SourceConfig, load_source_config
from scrapers.static_scraper import StaticScraper

SIMPLE_HTML = """
<html><body>
<div class="result">
  <a class="business-name">Acme Plumbing</a>
  <div class="phones">(555) 123-4567</div>
  <div class="adr">123 Main St, New York, NY</div>
</div>
<div class="result">
  <a class="business-name">Best Electric</a>
  <div class="phones">(555) 987-6543</div>
  <div class="adr">456 Oak Ave, Brooklyn, NY</div>
</div>
<div class="result">
  <a class="business-name">City Services</a>
  <div class="phones">(555) 555-0000</div>
</div>
</body></html>
"""

YP_YAML = """
name: test_yp
base_url: "https://www.yellowpages.com/search"
renderer: static
search_params:
  search_terms: "{query}"
  geo_location_terms: "{location}"
pagination:
  type: url_param
  param: page
  start: 1
  max_pages: 2
listing_selector: "div.result"
selectors:
  company_name: "a.business-name::text"
  phone: "div.phones::text"
  address: "div.adr::text"
rate_limit:
  delay_range: [0.01, 0.02]
  concurrent: 1
  max_retries: 1
proxy:
  required: false
"""


@pytest.fixture
def config(tmp_path):
    p = tmp_path / "test_yp.yaml"
    p.write_text(YP_YAML)
    return load_source_config("test_yp", tmp_path)


@pytest.fixture
def cached_scraper(tmp_path, config):
    cache = HtmlCache(tmp_path / "cache")
    cache.put(config.name, "plumbers", "New York", 0, SIMPLE_HTML)
    cache.put(config.name, "plumbers", "New York", 1, SIMPLE_HTML)
    return StaticScraper(cache=cache)


class TestStaticScraper:
    @pytest.mark.asyncio
    async def test_extracts_from_cached_html(self, cached_scraper, config):
        result = await cached_scraper.scrape(config, "plumbers", "New York", 100)
        assert isinstance(result, ScrapeResult)
        assert len(result.items) >= 3
        assert result.items[0]["company_name"] == "Acme Plumbing"
        assert result.items[0]["phone"] == "(555) 123-4567"

    @pytest.mark.asyncio
    async def test_respects_limit(self, cached_scraper, config):
        result = await cached_scraper.scrape(config, "plumbers", "New York", 2)
        assert len(result.items) <= 2

    @pytest.mark.asyncio
    async def test_returns_scrape_result_metadata(self, cached_scraper, config):
        result = await cached_scraper.scrape(config, "plumbers", "New York", 100)
        assert result.pages_scraped >= 1
        assert result.source == "test_yp"
        assert result.total_time_seconds > 0

    @pytest.mark.asyncio
    async def test_items_have_source_and_scraped_at(self, cached_scraper, config):
        result = await cached_scraper.scrape(config, "plumbers", "New York", 100)
        for item in result.items:
            assert item["source"] == "test_yp"
            assert "scraped_at" in item
            assert "source_url" in item

    def test_build_url_param(self, config):
        scraper = StaticScraper()
        url = scraper._build_url(config, "plumbers", "New York, NY", 0)
        assert "search_terms=plumbers" in url
        assert "page=1" in url

    def test_build_url_offset(self, tmp_path):
        yaml_content = YP_YAML.replace("type: url_param\n  param: page\n  start: 1\n  max_pages: 2",
                                        "type: offset\n  param: start\n  start: 0\n  step: 10\n  max_pages: 2")
        p = tmp_path / "off.yaml"
        p.write_text(yaml_content)
        config = load_source_config("off", tmp_path)
        scraper = StaticScraper()
        url = scraper._build_url(config, "test", "test", 1)
        assert "start=10" in url

    def test_build_url_template(self, tmp_path):
        yaml_content = """
name: clutch
url_template: "https://clutch.co/{category}?page={page}"
renderer: static
search_params: {}
pagination:
  type: url_param
  param: page
  start: 1
  max_pages: 2
listing_selector: "li.row"
selectors:
  name: "h3 a::text"
rate_limit:
  delay_range: [0.01, 0.02]
  concurrent: 1
  max_retries: 1
proxy:
  required: false
"""
        p = tmp_path / "clutch.yaml"
        p.write_text(yaml_content)
        config = load_source_config("clutch", tmp_path)
        scraper = StaticScraper()
        url = scraper._build_url(config, "developers", "NY", 0)
        assert "clutch.co/developers" in url
        assert "page=1" in url

    def test_url_encodes_query(self, config):
        scraper = StaticScraper()
        url = scraper._build_url(config, "web developers", "New York, NY", 0)
        assert "web+developers" in url or "web%20developers" in url

    def test_gaussian_delay_positive(self):
        for _ in range(100):
            delay = StaticScraper._gaussian_delay([2.0, 4.0])
            assert delay >= 0

    def test_scrape_sync(self, cached_scraper, config):
        result = cached_scraper.scrape_sync(config, "plumbers", "New York", 10)
        assert isinstance(result, ScrapeResult)
        assert len(result.items) > 0
