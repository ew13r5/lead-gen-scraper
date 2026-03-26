import time
from unittest.mock import patch

import pytest

from anti_detection.proxy_rotator import Proxy, ProxyRotator


@pytest.fixture
def proxy_file(tmp_path):
    p = tmp_path / "proxies.txt"
    p.write_text("host1:8080:user1:pass1\nhost2:8081:user2:pass2\nhost3:8082:user3:pass3\n")
    return p


class TestProxyRotator:
    def test_load_proxies(self, proxy_file):
        rotator = ProxyRotator(proxy_file)
        assert rotator.healthy_count == 3

    def test_round_robin(self, proxy_file):
        rotator = ProxyRotator(proxy_file)
        hosts = [rotator.get_next().host for _ in range(6)]
        assert hosts == ["host1", "host2", "host3", "host1", "host2", "host3"]

    def test_mark_failure_quarantines(self, proxy_file):
        rotator = ProxyRotator(proxy_file, max_consecutive_errors=3, quarantine_seconds=60)
        proxy = rotator.get_next()
        for _ in range(3):
            rotator.mark_failure(proxy)
        assert proxy.disabled_until > time.time()
        assert rotator.healthy_count == 2

    def test_quarantined_proxy_skipped(self, proxy_file):
        rotator = ProxyRotator(proxy_file, max_consecutive_errors=1, quarantine_seconds=60)
        p1 = rotator.get_next()
        rotator.mark_failure(p1)
        # Next calls should skip p1
        p2 = rotator.get_next()
        assert p2.host != p1.host

    def test_proxy_recovers_after_quarantine(self, proxy_file):
        rotator = ProxyRotator(proxy_file, max_consecutive_errors=1, quarantine_seconds=1)
        p1 = rotator.get_next()
        rotator.mark_failure(p1)
        assert rotator.healthy_count == 2
        # Fast-forward time
        p1.disabled_until = time.time() - 1
        assert rotator.healthy_count == 3

    def test_mark_success_resets_errors(self, proxy_file):
        rotator = ProxyRotator(proxy_file, max_consecutive_errors=3)
        proxy = rotator.get_next()
        rotator.mark_failure(proxy)
        rotator.mark_failure(proxy)
        assert proxy.consecutive_errors == 2
        rotator.mark_success(proxy)
        assert proxy.consecutive_errors == 0

    def test_all_quarantined_returns_none(self, proxy_file):
        rotator = ProxyRotator(proxy_file, max_consecutive_errors=1, quarantine_seconds=60)
        for _ in range(3):
            p = rotator.get_next()
            rotator.mark_failure(p)
        assert rotator.get_next() is None

    def test_empty_file_returns_none(self, tmp_path):
        empty = tmp_path / "empty.txt"
        empty.write_text("")
        rotator = ProxyRotator(empty)
        assert rotator.get_next() is None
        assert rotator.healthy_count == 0

    def test_malformed_line_skipped(self, tmp_path):
        f = tmp_path / "proxies.txt"
        f.write_text("host1:8080:user1:pass1\njust-a-host\n\nhost2:8081:user2:pass2\n")
        rotator = ProxyRotator(f)
        assert rotator.healthy_count == 2
