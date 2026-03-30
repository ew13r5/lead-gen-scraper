from anti_detection.stealth_config import get_browser_args, get_context_options


class TestStealthConfig:
    def test_browser_args_has_automation_control_disabled(self):
        args = get_browser_args()
        assert "--disable-blink-features=AutomationControlled" in args

    def test_context_options_viewport(self):
        opts = get_context_options("Mozilla/5.0 Test")
        assert opts["viewport"] == {"width": 1920, "height": 1080}

    def test_context_options_user_agent(self):
        opts = get_context_options("My UA String")
        assert opts["user_agent"] == "My UA String"

    def test_context_options_locale_and_timezone(self):
        opts = get_context_options("ua")
        assert opts["locale"] == "en-US"
        assert opts["timezone_id"] == "America/New_York"
