from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class PipelineStat(Base):
    __tablename__ = "pipeline_stats"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id: Mapped[str] = mapped_column(String(36), ForeignKey("scrape_tasks.id"), nullable=False)
    stage: Mapped[str] = mapped_column(String(50), nullable=False)
    count_in: Mapped[int] = mapped_column(Integer, default=0)
    count_out: Mapped[int] = mapped_column(Integer, default=0)
    count_removed: Mapped[int] = mapped_column(Integer, default=0)
    count_modified: Mapped[int] = mapped_column(Integer, default=0)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
