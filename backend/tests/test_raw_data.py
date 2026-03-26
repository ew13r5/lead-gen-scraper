import json

import pytest
from pydantic import ValidationError

from models.raw_data import ProgressInfo, RawCompanyData, ScrapeResult


class TestRawCompanyData:
    def test_accepts_valid_data(self, valid_company_data):
        record = RawCompanyData(**valid_company_data)
        assert record.company_name == "Acme Plumbing Services LLC"
        assert record.phone == "(555) 123-4567"
        assert record.rating == "4.7"
        assert record.review_count == 142

    def test_requires_company_name(self, minimal_company_data):
        del minimal_company_data["company_name"]
        with pytest.raises(ValidationError):
            RawCompanyData(**minimal_company_data)

    def test_requires_source(self, minimal_company_data):
        del minimal_company_data["source"]
        with pytest.raises(ValidationError):
            RawCompanyData(**minimal_company_data)

    def test_requires_source_url(self, minimal_company_data):
        del minimal_company_data["source_url"]
        with pytest.raises(ValidationError):
            RawCompanyData(**minimal_company_data)

    def test_requires_scraped_at(self, minimal_company_data):
        del minimal_company_data["scraped_at"]
        with pytest.raises(ValidationError):
            RawCompanyData(**minimal_company_data)

    def test_allows_none_for_optional_fields(self, minimal_company_data):
        record = RawCompanyData(**minimal_company_data)
        assert record.phone is None
        assert record.email is None
        assert record.website is None
        assert record.address is None
        assert record.city is None
        assert record.state is None
        assert record.category is None
        assert record.rating is None
        assert record.review_count is None

    def test_model_dump_json_serializable(self, valid_company_data):
        record = RawCompanyData(**valid_company_data)
        dumped = record.model_dump()
        serialized = json.dumps(dumped)
        assert isinstance(serialized, str)

    def test_scraped_at_accepts_iso8601(self, minimal_company_data):
        minimal_company_data["scraped_at"] = "2026-03-26T12:00:00Z"
        record = RawCompanyData(**minimal_company_data)
        assert record.scraped_at == "2026-03-26T12:00:00Z"


class TestScrapeResult:
    def test_accepts_valid_data(self):
        result = ScrapeResult(
            items=[{"company_name": "Test"}],
            pages_scraped=5,
            source="yellowpages",
            total_time_seconds=23.4,
        )
        assert result.pages_scraped == 5
        assert result.source == "yellowpages"

    def test_items_is_list_of_dicts(self):
        result = ScrapeResult(
            items=[{"a": 1}, {"b": 2}],
            pages_scraped=1,
            source="test",
            total_time_seconds=1.0,
        )
        assert isinstance(result.items, list)
        assert all(isinstance(item, dict) for item in result.items)

    def test_errors_defaults_to_empty_list(self):
        result = ScrapeResult(
            items=[],
            pages_scraped=0,
            source="test",
            total_time_seconds=0.0,
        )
        assert result.errors == []
        assert result.pages_skipped == 0


class TestProgressInfo:
    def test_accepts_valid_data(self):
        info = ProgressInfo(
            pages_processed=5,
            pages_total=20,
            items_found=87,
            errors=0,
            current_page=5,
        )
        assert info.pages_processed == 5
        assert info.pages_total == 20

    def test_pages_total_can_be_none(self):
        info = ProgressInfo(
            pages_processed=3,
            items_found=30,
            errors=0,
            current_page=3,
        )
        assert info.pages_total is None
