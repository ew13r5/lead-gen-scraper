from __future__ import annotations

import re
import shutil
from pathlib import Path


class HtmlCache:
    def __init__(self, cache_dir: Path) -> None:
        self._cache_dir = cache_dir

    def get(self, source: str, query: str, location: str, page: int) -> str | None:
        path = self._build_path(source, query, location, page)
        if path.exists():
            return path.read_text(encoding="utf-8")
        return None

    def put(self, source: str, query: str, location: str, page: int, html: str) -> None:
        path = self._build_path(source, query, location, page)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")

    def has(self, source: str, query: str, location: str, page: int) -> bool:
        return self._build_path(source, query, location, page).exists()

    def clear(self, source: str | None = None) -> int:
        count = 0
        if source:
            source_dir = self._cache_dir / source
            if source_dir.exists():
                for f in source_dir.glob("*.html"):
                    f.unlink()
                    count += 1
                if not any(source_dir.iterdir()):
                    source_dir.rmdir()
        else:
            if self._cache_dir.exists():
                for source_dir in self._cache_dir.iterdir():
                    if source_dir.is_dir():
                        for f in source_dir.glob("*.html"):
                            f.unlink()
                            count += 1
        return count

    def _build_path(self, source: str, query: str, location: str, page: int) -> Path:
        slug_q = self._slugify(query)
        slug_l = self._slugify(location)
        filename = f"{slug_q}_{slug_l}_page{page}.html"
        return self._cache_dir / source / filename

    @staticmethod
    def _slugify(text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^a-z0-9-]", "-", text)
        text = re.sub(r"-+", "-", text)
        text = text.strip("-")
        return text[:50]
