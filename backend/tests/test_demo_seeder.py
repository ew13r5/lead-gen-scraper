from demo.demo_seeder import seed_demo, CATEGORIES


class TestSeedDemo:
    def test_returns_correct_count(self):
        records = seed_demo(200, 3, seed=42)
        assert len(records) == 200

    def test_required_fields(self):
        records = seed_demo(10, 2, seed=42)
        for r in records:
            assert r["company_name"]
            assert r["source"]
            assert r["scraped_at"]

    def test_distributed_across_sources(self):
        records = seed_demo(100, 3, seed=42)
        sources = {r["source"] for r in records}
        assert len(sources) == 3

    def test_varied_phone_formats(self):
        records = seed_demo(100, 2, seed=42)
        phones = [r["phone"] for r in records if r.get("phone")]
        formats = set()
        for p in phones:
            if p.startswith("("):
                formats.add("parens")
            elif p.startswith("+"):
                formats.add("e164")
            elif "-" in p:
                formats.add("dashed")
            else:
                formats.add("digits")
        assert len(formats) >= 2

    def test_categories_from_list(self):
        records = seed_demo(50, 2, seed=42)
        for r in records:
            assert r["category"] in CATEGORIES
