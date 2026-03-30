from __future__ import annotations


async def apply_stealth(page) -> None:
    """Apply playwright-stealth evasions to a page."""
    try:
        from playwright_stealth import stealth_async
        await stealth_async(page)
    except ImportError:
        pass


def get_browser_args() -> list[str]:
    """Return Chromium launch arguments for anti-detection."""
    return [
        "--disable-blink-features=AutomationControlled",
        "--disable-extensions",
        "--disable-infobars",
        "--no-first-run",
    ]


def get_context_options(user_agent: str) -> dict:
    """Return browser context options with realistic fingerprint."""
    return {
        "user_agent": user_agent,
        "viewport": {"width": 1920, "height": 1080},
        "locale": "en-US",
        "timezone_id": "America/New_York",
    }
