from __future__ import annotations

import copy
import logging
import time
import uuid
from abc import ABC, abstractmethod

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class PipelineConfig(BaseModel):
    skip_stages: list[str] = []
    enrich: bool = False
    dedup_auto_threshold: int = 90
    dedup_review_threshold: int = 85
    check_email_dns: bool = True


class StageResult(BaseModel):
    stage_name: str
    count_in: int
    count_out: int
    count_removed: int = 0
    count_modified: int = 0
    duration_ms: int = 0
    details: dict = {}
    error: str | None = None


class PipelineStage(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def process(self, data: list[dict]) -> list[dict]: ...

    def run(self, data: list[dict]) -> tuple[list[dict], StageResult]:
        count_in = len(data)
        snapshots = {}
        for record in data:
            pid = record.get("_pipeline_id")
            if pid:
                snapshots[pid] = dict(record)

        start = time.perf_counter()
        try:
            result_data = self.process(data)
        except Exception as e:
            duration_ms = int((time.perf_counter() - start) * 1000)
            return data, StageResult(
                stage_name=self.name,
                count_in=count_in,
                count_out=count_in,
                count_removed=0,
                count_modified=0,
                duration_ms=duration_ms,
                error=str(e),
            )

        duration_ms = int((time.perf_counter() - start) * 1000)

        count_modified = 0
        for record in result_data:
            pid = record.get("_pipeline_id")
            if pid and pid in snapshots:
                old = snapshots[pid]
                if record != old:
                    count_modified += 1
            elif pid:
                count_modified += 1

        count_out = len(result_data)
        return result_data, StageResult(
            stage_name=self.name,
            count_in=count_in,
            count_out=count_out,
            count_removed=count_in - count_out,
            count_modified=count_modified,
            duration_ms=duration_ms,
        )


class PipelineRunner:
    def __init__(
        self,
        stages: list[PipelineStage],
        config: PipelineConfig | None = None,
    ) -> None:
        self.stages = stages
        self.config = config or PipelineConfig()

    def run(self, data: list[dict]) -> tuple[list[dict], list[StageResult]]:
        # Pre-validation: filter records without company_name
        valid_data = []
        for record in data:
            cn = record.get("company_name")
            if not cn:
                logger.warning("Skipping record without company_name")
                continue
            # Coerce phone to str if needed
            if "phone" in record and record["phone"] is not None:
                if not isinstance(record["phone"], str):
                    record["phone"] = str(record["phone"])
            valid_data.append(record)

        data = valid_data

        # Assign _pipeline_id to records missing it
        for record in data:
            if "_pipeline_id" not in record:
                record["_pipeline_id"] = str(uuid.uuid4())

        results: list[StageResult] = []
        for stage in self.stages:
            if stage.name in self.config.skip_stages:
                continue
            data, result = stage.run(data)
            results.append(result)
            if result.error:
                logger.error("Stage %s failed: %s", stage.name, result.error)
                break

        return data, results
