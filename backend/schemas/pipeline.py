from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class PipelineStageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    stage: str
    count_in: int
    count_out: int
    count_removed: int
    count_modified: int
    duration_ms: int | None = None
    details: dict | None = None


class PipelineResponse(BaseModel):
    task_id: str
    stages: list[PipelineStageResponse]
