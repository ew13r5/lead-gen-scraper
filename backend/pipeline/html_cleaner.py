from __future__ import annotations

import html
import re

from pipeline.base import PipelineStage

_ZERO_WIDTH = re.compile("[\u200b\u200c\u200d\ufeff]")
_WHITESPACE = re.compile(r"\s+")


def clean_text(value: str) -> str:
    value = html.unescape(value)
    value = _ZERO_WIDTH.sub("", value)
    value = value.replace("\u00ad", "")
    value = value.replace("\u00a0", " ")
    value = _WHITESPACE.sub(" ", value).strip()
    return value


class HTMLCleaner(PipelineStage):
    @property
    def name(self) -> str:
        return "html_cleaner"

    def process(self, data: list[dict]) -> list[dict]:
        for record in data:
            for key, value in record.items():
                if isinstance(value, str):
                    record[key] = clean_text(value)
        return data
