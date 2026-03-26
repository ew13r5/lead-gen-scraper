import pytest
from pipeline.html_cleaner import HTMLCleaner


@pytest.fixture
def cleaner():
    return HTMLCleaner()


def rec(**kw):
    return {"company_name": "Test", "_pipeline_id": "id-1", **kw}


class TestHTMLCleaner:
    def test_html_entities(self, cleaner):
        data = [rec(company_name="Smith &amp; Johnson&#39;s &lt;Corp&gt;")]
        result, _ = cleaner.run(data)
        assert result[0]["company_name"] == "Smith & Johnson's <Corp>"

    def test_zero_width_chars(self, cleaner):
        data = [rec(address="123\u200b Main\u200c St\u200d\ufeff")]
        result, _ = cleaner.run(data)
        assert result[0]["address"] == "123 Main St"

    def test_soft_hyphens(self, cleaner):
        data = [rec(company_name="Acme\u00adPlumbing")]
        result, _ = cleaner.run(data)
        assert result[0]["company_name"] == "AcmePlumbing"

    def test_nbsp_normalized(self, cleaner):
        data = [rec(address="123\u00a0Main\u00a0St")]
        result, _ = cleaner.run(data)
        assert result[0]["address"] == "123 Main St"

    def test_whitespace_collapsed(self, cleaner):
        data = [rec(company_name="  Acme   Plumbing  \n Services  ")]
        result, _ = cleaner.run(data)
        assert result[0]["company_name"] == "Acme Plumbing Services"

    def test_leading_trailing_stripped(self, cleaner):
        data = [rec(company_name="  Hello  ")]
        result, _ = cleaner.run(data)
        assert result[0]["company_name"] == "Hello"

    def test_non_string_fields_untouched(self, cleaner):
        data = [rec(review_count=42, rating=None)]
        result, _ = cleaner.run(data)
        assert result[0]["review_count"] == 42
        assert result[0]["rating"] is None

    def test_clean_record_not_modified(self, cleaner):
        data = [rec(company_name="Already Clean")]
        _, stage_result = cleaner.run(data)
        assert stage_result.count_modified == 0

    def test_count_modified_tracks(self, cleaner):
        data = [rec(company_name="Test &amp; Co"), rec(company_name="Clean", _pipeline_id="id-2")]
        _, stage_result = cleaner.run(data)
        assert stage_result.count_modified == 1

    def test_records_never_removed(self, cleaner):
        data = [rec(), rec(_pipeline_id="id-2")]
        _, stage_result = cleaner.run(data)
        assert stage_result.count_in == stage_result.count_out
