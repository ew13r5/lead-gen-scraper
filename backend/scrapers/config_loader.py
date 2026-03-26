from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal, Union

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator


class UrlParamPagination(BaseModel):
    type: Literal["url_param"]
    param: str
    start: int
    max_pages: int


class OffsetPagination(BaseModel):
    type: Literal["offset"]
    param: str
    start: int
    step: int
    max_pages: int


PaginationUnion = Annotated[
    Union[UrlParamPagination, OffsetPagination],
    Field(discriminator="type"),
]


class JsonLdConfig(BaseModel):
    selector: str = "script[type='application/ld+json']"
    fields_map: dict[str, str]


class RateLimitConfig(BaseModel):
    delay_range: list[float]
    concurrent: int
    max_retries: int


class ProxyConfig(BaseModel):
    required: bool
    country: str | None = None


class SourceConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    base_url: str = ""
    renderer: Literal["static", "playwright"]
    search_params: dict[str, str] = {}
    url_template: str | None = None
    pagination: PaginationUnion
    listing_selector: str
    selectors: dict[str, str]
    json_ld: JsonLdConfig | None = None
    rate_limit: RateLimitConfig
    proxy: ProxyConfig

    @model_validator(mode="after")
    def validate_config_rules(self) -> "SourceConfig":
        if self.renderer == "playwright":
            raise ValueError(
                "Playwright renderer not supported in Phase 1. Use renderer: static"
            )

        dr = self.rate_limit.delay_range
        if len(dr) != 2:
            raise ValueError("delay_range must have exactly 2 elements [min, max]")
        if dr[0] > dr[1]:
            raise ValueError(
                f"delay_range[0] ({dr[0]}) must be <= delay_range[1] ({dr[1]})"
            )

        if self.url_template is not None and "{page}" not in self.url_template:
            raise ValueError("url_template must contain {page} placeholder")

        if not self.base_url and self.url_template is None:
            raise ValueError(
                "Either base_url or url_template must be provided"
            )

        return self


def load_source_config(source_name: str, sources_dir: Path) -> SourceConfig:
    """Load and validate a YAML source config by name."""
    path = sources_dir / f"{source_name}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Source config not found: {path}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return SourceConfig(**raw)


def load_all_configs(sources_dir: Path) -> dict[str, SourceConfig]:
    """Load all YAML configs from directory."""
    configs = {}
    for path in sorted(sources_dir.glob("*.yaml")):
        name = path.stem
        configs[name] = load_source_config(name, sources_dir)
    return configs


def validate_config(source_name: str, sources_dir: Path) -> list[str]:
    """Validate config and return human-readable error strings. Never raises."""
    try:
        load_source_config(source_name, sources_dir)
        return []
    except FileNotFoundError as e:
        return [str(e)]
    except ValidationError as e:
        errors = []
        for err in e.errors():
            loc = ".".join(str(part) for part in err["loc"])
            msg = err["msg"]
            val = err.get("input", "N/A")
            errors.append(f"{loc}: {msg} (got: {val!r})")
        return errors
