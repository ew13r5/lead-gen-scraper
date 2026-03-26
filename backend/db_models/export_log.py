from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class ExportLog(Base):
    __tablename__ = "export_log"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id: Mapped[str] = mapped_column(String(36), ForeignKey("scrape_tasks.id"), nullable=False)
    format: Mapped[str] = mapped_column(String(20), nullable=False)
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    rows_exported: Mapped[int] = mapped_column(Integer, default=0)
    exported_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
