from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    source: str
    query: str
    location: str
    limit: int = Field(default=100, ge=1, le=10000)
    enrich: bool = False


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    source: str
    query: str
    location: str
    limit: int | None
    mode: str
    status: str
    total_scraped: int
    total_cleaned: int
    total_deduped: int
    total_exported: int
    started_at: datetime | None
    completed_at: datetime | None
    error_message: str | None
    created_at: datetime


class TaskListResponse(BaseModel):
    items: list[TaskResponse]
    total: int
    page: int
    page_size: int
