from pydantic import BaseModel


class PipelineStats(BaseModel):
    """Per-stage pipeline statistics for DB persistence.

    Split 03 (API backend) maps this to a SQLAlchemy model for PostgreSQL storage.
    """

    task_id: str | None = None
    stage: str
    count_in: int
    count_out: int
    count_removed: int
    count_modified: int
    duration_ms: int
    details: dict = {}
