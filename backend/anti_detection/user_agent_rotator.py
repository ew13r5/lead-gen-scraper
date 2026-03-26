from __future__ import annotations

from .headers import HEADER_PROFILES


class UserAgentRotator:
    def __init__(self) -> None:
        self._profiles = HEADER_PROFILES
        self._index = -1

    def get_headers(self) -> dict[str, str]:
        self._index = (self._index + 1) % len(self._profiles)
        return dict(self._profiles[self._index])
