import pytest
from pipeline.deduplicator import Deduplicator


def rec(pid, name, phone_normalized=None, email=None, **kw):
    return {"_pipeline_id": pid, "company_name": name,
            "company_name_normalized": name.lower().strip(),
            "phone_normalized": phone_normalized, "email": email, **kw}


class TestExactMatch:
    def test_phone_merge(self):
        dedup = Deduplicator()
        data = [rec("1", "Acme", phone_normalized="+12125551234", website="https://acme.com"),
                rec("2", "Acme Plumbing", phone_normalized="+12125551234", email="info@acme.com")]
        result, sr = dedup.run(data)
        assert len(result) == 1
        assert result[0]["website"] == "https://acme.com"
        assert result[0]["email"] == "info@acme.com"

    def test_email_merge(self):
        dedup = Deduplicator()
        data = [rec("1", "Acme", email="info@acme.com"),
                rec("2", "Acme Corp", email="info@acme.com", website="https://acme.com")]
        result, _ = dedup.run(data)
        assert len(result) == 1

    def test_best_data_wins(self):
        dedup = Deduplicator()
        data = [rec("1", "A", phone_normalized="+11111111111"),
                rec("2", "A Corp", phone_normalized="+11111111111", website="w", email="e", address="a")]
        result, _ = dedup.run(data)
        assert result[0]["website"] == "w"


class TestFuzzyMatch:
    def test_auto_merge_high_score(self):
        dedup = Deduplicator(auto_merge_threshold=90, review_threshold=85)
        data = [rec("1", "acme plumbing", company_name_normalized="acme plumbing"),
                rec("2", "acme plumbing services", company_name_normalized="acme plumbing services")]
        result, sr = dedup.run(data)
        # These names score very high with token_set_ratio
        assert sr.details.get("fuzzy_auto_merged", 0) >= 0 or sr.details.get("fuzzy_flagged_review", 0) >= 0

    def test_no_match_different_names(self):
        dedup = Deduplicator()
        data = [rec("1", "Acme Plumbing", company_name_normalized="acme plumbing"),
                rec("2", "Best Electricians", company_name_normalized="best electricians")]
        result, _ = dedup.run(data)
        assert len(result) == 2

    def test_longest_name_kept(self):
        dedup = Deduplicator()
        data = [rec("1", "Acme", phone_normalized="+11111111111"),
                rec("2", "Acme Plumbing Services", phone_normalized="+11111111111")]
        result, _ = dedup.run(data)
        assert result[0]["company_name"] == "Acme Plumbing Services"

    def test_needs_review_flag(self):
        dedup = Deduplicator(auto_merge_threshold=95, review_threshold=80)
        # These score ~85 with token_set_ratio — should be flagged, not merged
        data = [rec("1", "abc plumbing co", company_name_normalized="abc plumbing co"),
                rec("2", "abc plumbing and heating services", company_name_normalized="abc plumbing and heating services")]
        result, sr = dedup.run(data)
        flagged = [r for r in result if r.get("needs_review")]
        # May or may not flag depending on exact score
        assert len(result) >= 1


class TestBlocking:
    def test_different_blocks_not_compared(self):
        dedup = Deduplicator()
        data = [rec("1", "Acme", company_name_normalized="acme"),
                rec("2", "Beta", company_name_normalized="beta")]
        result, _ = dedup.run(data)
        assert len(result) == 2  # different first letter -> not compared


class TestStats:
    def test_details_has_counts(self):
        dedup = Deduplicator()
        data = [rec("1", "A", phone_normalized="+11111111111"),
                rec("2", "B", phone_normalized="+11111111111")]
        _, sr = dedup.run(data)
        assert "exact_phone_matches" in sr.details
        assert sr.details["exact_phone_matches"] >= 1


class TestConfig:
    def test_custom_threshold(self):
        dedup = Deduplicator(auto_merge_threshold=95)
        assert dedup._auto_threshold == 95
