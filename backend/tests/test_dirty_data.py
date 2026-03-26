from demo.demo_seeder import seed_demo
from demo.dirty_data_generator import make_dirty


class TestMakeDirty:
    def test_duplicates_added(self):
        clean = seed_demo(200, 3, seed=42)
        dirty = make_dirty(clean, seed=42)
        # ~15% dupes -> output ~215-240 records
        assert len(dirty) > len(clean)
        assert len(dirty) < len(clean) * 1.25

    def test_invalid_emails(self):
        clean = seed_demo(200, 3, seed=42)
        dirty = make_dirty(clean, seed=42)
        invalid = sum(1 for r in dirty if r.get("email") and "@" not in r["email"])
        # ~10% of 200 base records = ~20, but probabilistic
        assert invalid >= 5

    def test_html_entities(self):
        clean = seed_demo(200, 3, seed=42)
        dirty = make_dirty(clean, seed=42)
        has_entities = sum(1 for r in dirty if "&amp;" in r.get("company_name", ""))
        assert has_entities >= 2

    def test_unicode_issues(self):
        clean = seed_demo(200, 3, seed=42)
        dirty = make_dirty(clean, seed=42)
        has_zws = sum(1 for r in dirty if "\u200b" in r.get("address", ""))
        has_nbsp = sum(1 for r in dirty if "\u00a0" in r.get("company_name", ""))
        assert has_zws + has_nbsp >= 2

    def test_output_count_approximate(self):
        clean = seed_demo(100, 2, seed=42)
        dirty = make_dirty(clean, seed=42)
        assert 100 <= len(dirty) <= 130
