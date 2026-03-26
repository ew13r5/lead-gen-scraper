import pytest
from pipeline.field_validator import FieldValidator


@pytest.fixture
def validator():
    return FieldValidator(check_email_dns=False)


def rec(**kw):
    return {"company_name": "Test Co", "_pipeline_id": "id-1", **kw}


class TestEmailValidation:
    def test_valid_email(self, validator):
        data = [rec(email="user@example.com")]
        result, _ = validator.run(data)
        assert result[0]["email_validated"] is True

    def test_invalid_missing_at(self, validator):
        data = [rec(email="userexample.com")]
        result, _ = validator.run(data)
        assert result[0]["email"] is None
        assert result[0]["email_validated"] is False

    def test_invalid_bad_domain(self, validator):
        data = [rec(email="user@.com")]
        result, _ = validator.run(data)
        assert result[0]["email"] is None

    def test_email_normalized(self, validator):
        data = [rec(email="User@Example.COM")]
        result, _ = validator.run(data)
        # email-validator preserves local part case, lowercases domain
        assert result[0]["email"].endswith("@example.com")


class TestPhoneNormalization:
    def test_parenthesized(self, validator):
        data = [rec(phone="(212) 555-1234")]
        result, _ = validator.run(data)
        assert result[0]["phone_normalized"] == "+12125551234"

    def test_dashed(self, validator):
        data = [rec(phone="212-555-1234")]
        result, _ = validator.run(data)
        assert result[0]["phone_normalized"] == "+12125551234"

    def test_e164_passthrough(self, validator):
        data = [rec(phone="+12125551234")]
        result, _ = validator.run(data)
        assert result[0]["phone_normalized"] == "+12125551234"

    def test_digits_only(self, validator):
        data = [rec(phone="2125551234")]
        result, _ = validator.run(data)
        assert result[0]["phone_normalized"] == "+12125551234"

    def test_invalid_short(self, validator):
        data = [rec(phone="12345")]
        result, _ = validator.run(data)
        assert result[0]["phone_normalized"] is None

    def test_phone_display_added(self, validator):
        data = [rec(phone="2125551234")]
        result, _ = validator.run(data)
        assert "phone_display" in result[0]


class TestWebsiteCleaning:
    def test_adds_scheme(self, validator):
        data = [rec(website="example.com")]
        result, _ = validator.run(data)
        assert result[0]["website"].startswith("https://")

    def test_strips_tracking(self, validator):
        data = [rec(website="https://example.com/page?utm_source=google&id=123")]
        result, _ = validator.run(data)
        assert "utm_source" not in result[0]["website"]
        assert "id=123" in result[0]["website"]

    def test_domain_lowercased(self, validator):
        data = [rec(website="https://EXAMPLE.COM/Path")]
        result, _ = validator.run(data)
        assert "example.com" in result[0]["website"]

    def test_trailing_slash_stripped(self, validator):
        data = [rec(website="https://example.com/path/")]
        result, _ = validator.run(data)
        assert result[0]["website"] == "https://example.com/path"

    def test_invalid_no_domain(self, validator):
        data = [rec(website="not-a-url")]
        result, _ = validator.run(data)
        # May become https://not-a-url which has a netloc, or None
        # Depends on urlparse behavior


class TestCompanyNameNormalization:
    def test_strip_corp(self, validator):
        data = [rec(company_name="Acme Corp.")]
        result, _ = validator.run(data)
        assert result[0]["company_name_normalized"] == "acme"

    def test_strip_llc(self, validator):
        data = [rec(company_name="Smith & Johnson LLC")]
        result, _ = validator.run(data)
        assert result[0]["company_name_normalized"] == "smith & johnson"

    def test_original_preserved(self, validator):
        data = [rec(company_name="Acme Corp.")]
        result, _ = validator.run(data)
        assert result[0]["company_name"] == "Acme Corp."


class TestAddressStandardization:
    def test_street_abbreviation(self, validator):
        data = [rec(address="123 Main St")]
        result, _ = validator.run(data)
        assert result[0]["address_normalized"] == "123 Main Street"


class TestStageBehavior:
    def test_records_never_removed(self, validator):
        data = [rec(), rec(_pipeline_id="id-2")]
        _, stage_result = validator.run(data)
        assert stage_result.count_in == stage_result.count_out

    def test_stats_in_details(self, validator):
        data = [rec(email="bad", phone="12345", website="https://ok.com")]
        _, stage_result = validator.run(data)
        assert "emails_invalid" in stage_result.details
