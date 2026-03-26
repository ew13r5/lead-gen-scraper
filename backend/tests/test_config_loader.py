import pytest
import yaml
from pathlib import Path
from pydantic import ValidationError

from scrapers.config_loader import (
    SourceConfig,
    UrlParamPagination,
    OffsetPagination,
    load_source_config,
    load_all_configs,
    validate_config,
)

# --- Helper: write YAML to tmp file ---

VALID_YP_YAML = """
name: yellowpages
base_url: "https://www.yellowpages.com/search"
renderer: static
search_params:
  search_terms: "{query}"
  geo_location_terms: "{location}"
pagination:
  type: url_param
  param: page
  start: 1
  max_pages: 50
listing_selector: "div.result"
selectors:
  name: "a.business-name"
  phone: "div.phones"
rate_limit:
  delay_range: [2, 4]
  concurrent: 1
  max_retries: 3
proxy:
  required: true
  country: US
"""

VALID_YELP_YAML = """
name: yelp
base_url: "https://www.yelp.com/search"
renderer: static
search_params:
  find_desc: "{query}"
  find_loc: "{location}"
pagination:
  type: offset
  param: start
  start: 0
  step: 10
  max_pages: 100
listing_selector: "div[data-testid='serp-ia-card']"
selectors:
  name: "a.css-19v1rkv"
json_ld:
  selector: "script[type='application/ld+json']"
  fields_map:
    name: "name"
    address: "address.streetAddress"
rate_limit:
  delay_range: [3, 5]
  concurrent: 1
  max_retries: 3
proxy:
  required: true
"""

VALID_CLUTCH_YAML = """
name: clutch
url_template: "https://clutch.co/{category}?page={page}"
renderer: static
search_params: {}
pagination:
  type: url_param
  param: page
  start: 1
  max_pages: 50
listing_selector: "li.provider-row"
selectors:
  name: "h3.company_info a"
rate_limit:
  delay_range: [2, 4]
  concurrent: 1
  max_retries: 3
proxy:
  required: false
"""


def write_yaml(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / f"{name}.yaml"
    p.write_text(content)
    return p


class TestLoadSourceConfig:
    def test_valid_yellowpages(self, tmp_path):
        write_yaml(tmp_path, "yellowpages", VALID_YP_YAML)
        config = load_source_config("yellowpages", tmp_path)
        assert config.name == "yellowpages"
        assert config.base_url == "https://www.yellowpages.com/search"
        assert config.renderer == "static"
        assert config.listing_selector == "div.result"
        assert config.proxy.required is True
        assert config.proxy.country == "US"

    def test_valid_yelp_with_json_ld(self, tmp_path):
        write_yaml(tmp_path, "yelp", VALID_YELP_YAML)
        config = load_source_config("yelp", tmp_path)
        assert config.json_ld is not None
        assert config.json_ld.fields_map["name"] == "name"
        assert config.json_ld.fields_map["address"] == "address.streetAddress"

    def test_url_template_clutch(self, tmp_path):
        write_yaml(tmp_path, "clutch", VALID_CLUTCH_YAML)
        config = load_source_config("clutch", tmp_path)
        assert config.url_template == "https://clutch.co/{category}?page={page}"
        assert config.base_url == ""

    def test_missing_name_raises(self, tmp_path):
        bad = VALID_YP_YAML.replace("name: yellowpages\n", "")
        write_yaml(tmp_path, "bad", bad)
        with pytest.raises(ValidationError):
            load_source_config("bad", tmp_path)

    def test_extra_key_raises(self, tmp_path):
        bad = VALID_YP_YAML + "unknown_field: true\n"
        write_yaml(tmp_path, "bad", bad)
        with pytest.raises(ValidationError):
            load_source_config("bad", tmp_path)

    def test_playwright_renderer_raises(self, tmp_path):
        bad = VALID_YP_YAML.replace("renderer: static", "renderer: playwright")
        write_yaml(tmp_path, "bad", bad)
        with pytest.raises(ValidationError, match="[Pp]laywright"):
            load_source_config("bad", tmp_path)

    def test_delay_range_inverted_raises(self, tmp_path):
        bad = VALID_YP_YAML.replace("delay_range: [2, 4]", "delay_range: [5, 2]")
        write_yaml(tmp_path, "bad", bad)
        with pytest.raises(ValidationError, match="delay_range"):
            load_source_config("bad", tmp_path)

    def test_url_param_pagination(self, tmp_path):
        write_yaml(tmp_path, "yp", VALID_YP_YAML)
        config = load_source_config("yp", tmp_path)
        assert isinstance(config.pagination, UrlParamPagination)
        assert config.pagination.param == "page"

    def test_offset_pagination(self, tmp_path):
        write_yaml(tmp_path, "yelp", VALID_YELP_YAML)
        config = load_source_config("yelp", tmp_path)
        assert isinstance(config.pagination, OffsetPagination)
        assert config.pagination.step == 10

    def test_invalid_pagination_type(self, tmp_path):
        bad = VALID_YP_YAML.replace("type: url_param", "type: infinite_scroll")
        write_yaml(tmp_path, "bad", bad)
        with pytest.raises(ValidationError):
            load_source_config("bad", tmp_path)

    def test_nonexistent_source_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_source_config("nonexistent", tmp_path)

    def test_listing_selector_required(self, tmp_path):
        bad = VALID_YP_YAML.replace('listing_selector: "div.result"\n', "")
        write_yaml(tmp_path, "bad", bad)
        with pytest.raises(ValidationError):
            load_source_config("bad", tmp_path)


class TestLoadAllConfigs:
    def test_loads_all(self, tmp_path):
        write_yaml(tmp_path, "yellowpages", VALID_YP_YAML)
        write_yaml(tmp_path, "yelp", VALID_YELP_YAML)
        configs = load_all_configs(tmp_path)
        assert len(configs) == 2
        assert "yellowpages" in configs
        assert "yelp" in configs


class TestValidateConfig:
    def test_valid_returns_empty(self, tmp_path):
        write_yaml(tmp_path, "yp", VALID_YP_YAML)
        errors = validate_config("yp", tmp_path)
        assert errors == []

    def test_invalid_returns_dot_path_errors(self, tmp_path):
        bad = VALID_YP_YAML.replace("delay_range: [2, 4]", "delay_range: [5, 2]")
        write_yaml(tmp_path, "bad", bad)
        errors = validate_config("bad", tmp_path)
        assert len(errors) > 0
        assert any("delay_range" in e for e in errors)
