from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_name: Mapped[str] = mapped_column(String(500), nullable=False)
    company_name_normalized: Mapped[str | None] = mapped_column(String(500), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    phone_normalized: Mapped[str | None] = mapped_column(String(20), nullable=True)
    phone_display: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str | None] = mapped_column(String(200), nullable=True)
    email_validated: Mapped[bool] = mapped_column(Boolean, default=False)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    website_alive: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    address_normalized: Mapped[str | None] = mapped_column(String(500), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(10), nullable=True)
    zip: Mapped[str | None] = mapped_column(String(20), nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    review_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    scraped_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    enriched_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    social_links: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_duplicate_of: Mapped[str | None] = mapped_column(String(36), ForeignKey("companies.id"), nullable=True)
    needs_review: Mapped[bool] = mapped_column(Boolean, default=False)
    pipeline_id: Mapped[str | None] = mapped_column(String(36), unique=True, nullable=True)
    task_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("scrape_tasks.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, onupdate=func.now(), nullable=True)

    __table_args__ = (
        Index("ix_companies_source", "source"),
        Index("ix_companies_city", "city"),
        Index("ix_companies_state", "state"),
        Index("ix_companies_category", "category"),
        Index("ix_companies_task_id", "task_id"),
        Index("ix_companies_needs_review", "needs_review"),
    )
