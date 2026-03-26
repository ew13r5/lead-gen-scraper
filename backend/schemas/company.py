from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CompanyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_name: str
    phone_display: str | None = None
    email: str | None = None
    email_validated: bool = False
    website: str | None = None
    website_alive: bool | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zip: str | None = None
    category: str | None = None
    rating: float | None = None
    review_count: int | None = None
    source: str | None = None
    source_url: str | None = None
    social_links: dict | None = None
    needs_review: bool = False
    created_at: datetime | None = None


class CompanyListResponse(BaseModel):
    items: list[CompanyResponse]
    total: int
    page: int
    page_size: int
