from anti_detection.user_agent_rotator import UserAgentRotator

REQUIRED_KEYS = {
    "User-Agent", "Accept", "Accept-Language", "Accept-Encoding",
    "Sec-Ch-Ua", "Sec-Ch-Ua-Mobile", "Sec-Ch-Ua-Platform",
    "Sec-Fetch-Dest", "Sec-Fetch-Mode", "Sec-Fetch-Site",
    "Connection", "Upgrade-Insecure-Requests",
}


class TestUserAgentRotator:
    def test_get_headers_returns_user_agent(self):
        rotator = UserAgentRotator()
        headers = rotator.get_headers()
        assert "User-Agent" in headers
        assert "Mozilla" in headers["User-Agent"]

    def test_sec_ch_ua_matches_ua(self):
        rotator = UserAgentRotator()
        headers = rotator.get_headers()
        ua = headers["User-Agent"]
        sec_ch = headers["Sec-Ch-Ua"]
        if "Chrome/131" in ua:
            assert "131" in sec_ch
        elif "Chrome/130" in ua:
            assert "130" in sec_ch

    def test_platform_matches_ua(self):
        rotator = UserAgentRotator()
        headers = rotator.get_headers()
        ua = headers["User-Agent"]
        platform = headers["Sec-Ch-Ua-Platform"]
        if "Windows" in ua:
            assert "Windows" in platform
        elif "Macintosh" in ua:
            assert "macOS" in platform

    def test_rotation(self):
        rotator = UserAgentRotator()
        uas = {rotator.get_headers()["User-Agent"] for _ in range(10)}
        assert len(uas) > 1

    def test_all_required_keys(self):
        rotator = UserAgentRotator()
        headers = rotator.get_headers()
        assert REQUIRED_KEYS.issubset(headers.keys())
