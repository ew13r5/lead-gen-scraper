from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class ExportRequest(BaseModel):
    task_id: str
    format: Literal["csv", "excel", "json", "sheets"]
    options: dict | None = None


class ExportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    task_id: str
    format: str
    file_path: str | None = None
    rows_exported: int
    url: str | None = None
    exported_at: datetime
