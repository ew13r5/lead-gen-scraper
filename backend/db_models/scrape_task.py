from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class ScrapeTask(Base):
    __tablename__ = "scrape_tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    query: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(500), nullable=False)
    limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    enrich: Mapped[bool] = mapped_column(Boolean, default=False)
    mode: Mapped[str] = mapped_column(String(20), default="demo")
    status: Mapped[str] = mapped_column(String(20), default="pending")
    total_scraped: Mapped[int] = mapped_column(Integer, default=0)
    total_cleaned: Mapped[int] = mapped_column(Integer, default=0)
    total_deduped: Mapped[int] = mapped_column(Integer, default=0)
    total_exported: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
