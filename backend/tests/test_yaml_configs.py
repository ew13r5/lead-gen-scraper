import pytest
from pathlib import Path
from parsel import Selector

from scrapers.config_loader import load_all_configs, load_source_config

SOURCES_DIR = Path(__file__).parent.parent / "sources"
FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestConfigsLoad:
    def test_all_configs_load(self):
        configs = load_all_configs(SOURCES_DIR)
        assert len(configs) == 5
        assert set(configs.keys()) == {"yellowpages", "yelp", "bbb", "clutch", "crunchbase"}

    def test_each_has_listing_selector(self):
        configs = load_all_configs(SOURCES_DIR)
        for name, config in configs.items():
            assert config.listing_selector, f"{name} missing listing_selector"


class TestFixtureExtraction:
    def test_yellowpages_extracts_listings(self):
        config = load_source_config("yellowpages", SOURCES_DIR)
        html = (FIXTURES_DIR / "yellowpages_page1.html").read_text()
        sel = Selector(html)
        containers = sel.css(config.listing_selector)
        assert len(containers) >= 5
        name = containers[0].css(config.selectors["company_name"]).get()
        assert name and len(name) > 0

    def test_yelp_has_json_ld(self):
        config = load_source_config("yelp", SOURCES_DIR)
        assert config.json_ld is not None
        html = (FIXTURES_DIR / "yelp_page1.html").read_text()
        sel = Selector(html)
        scripts = sel.css(config.json_ld.selector)
        assert len(scripts) > 0

    def test_bbb_extracts_rating(self):
        config = load_source_config("bbb", SOURCES_DIR)
        html = (FIXTURES_DIR / "bbb_page1.html").read_text()
        sel = Selector(html)
        containers = sel.css(config.listing_selector)
        assert len(containers) >= 1
        rating = containers[0].css(config.selectors["rating"]).get()
        assert rating in ("A+", "A", "B+", "B", "C", "F")

    def test_clutch_extracts_hourly_rate(self):
        config = load_source_config("clutch", SOURCES_DIR)
        html = (FIXTURES_DIR / "clutch_page1.html").read_text()
        sel = Selector(html)
        containers = sel.css(config.listing_selector)
        assert len(containers) >= 1
        rate = containers[0].css(config.selectors["hourly_rate"]).get()
        assert rate and "$" in rate
