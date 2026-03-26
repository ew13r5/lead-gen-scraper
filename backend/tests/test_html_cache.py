import pytest
from cache.html_cache import HtmlCache


@pytest.fixture
def cache(tmp_path):
    return HtmlCache(cache_dir=tmp_path)


class TestHtmlCache:
    def test_put_then_get(self, cache):
        html = "<html><body>Test</body></html>"
        cache.put("yellowpages", "plumbers", "New York, NY", 1, html)
        result = cache.get("yellowpages", "plumbers", "New York, NY", 1)
        assert result == html

    def test_get_nonexistent_returns_none(self, cache):
        assert cache.get("yelp", "test", "test", 1) is None

    def test_has_true_for_cached(self, cache):
        cache.put("yp", "q", "l", 1, "<html/>")
        assert cache.has("yp", "q", "l", 1) is True

    def test_has_false_for_uncached(self, cache):
        assert cache.has("yp", "q", "l", 1) is False

    def test_creates_source_subdirectory(self, cache, tmp_path):
        cache.put("yellowpages", "test", "test", 1, "<html/>")
        assert (tmp_path / "yellowpages").is_dir()

    def test_clear_with_source(self, cache):
        cache.put("yp", "q", "l", 1, "<html/>")
        cache.put("yelp", "q", "l", 1, "<html/>")
        deleted = cache.clear(source="yp")
        assert deleted == 1
        assert cache.has("yp", "q", "l", 1) is False
        assert cache.has("yelp", "q", "l", 1) is True

    def test_clear_all(self, cache):
        cache.put("yp", "q", "l", 1, "<html/>")
        cache.put("yelp", "q", "l", 1, "<html/>")
        deleted = cache.clear()
        assert deleted == 2

    def test_special_characters_slugified(self, cache):
        cache.put("yp", "Plumbing & Heating", "New York, NY", 1, "<html/>")
        result = cache.get("yp", "Plumbing & Heating", "New York, NY", 1)
        assert result == "<html/>"

    def test_long_strings_truncated(self, cache):
        long_query = "a" * 100
        cache.put("yp", long_query, "test", 1, "<html/>")
        result = cache.get("yp", long_query, "test", 1)
        assert result == "<html/>"
