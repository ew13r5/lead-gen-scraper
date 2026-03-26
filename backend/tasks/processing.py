from __future__ import annotations

from datetime import datetime

from db_models.company import Company
from db_models.pipeline_stat import PipelineStat
from pipeline.base import PipelineRunner, PipelineConfig, StageResult
from pipeline.html_cleaner import HTMLCleaner
from pipeline.field_validator import FieldValidator
from pipeline.deduplicator import Deduplicator
from pipeline.enricher import Enricher

COMPANY_COLUMNS = set(Company.__table__.columns.keys())


def _map_dict_to_company(d: dict, task_id: str) -> Company:
    """Convert pipeline output dict to Company ORM instance."""
    fields: dict = {}

    for key, value in d.items():
        if key == "_pipeline_id":
            fields["pipeline_id"] = value
        elif key == "_needs_review":
            fields["needs_review"] = bool(value)
        elif key.startswith("_"):
            continue
        elif key == "rating" and value is not None:
            try:
                fields["rating"] = float(value)
            except (ValueError, TypeError):
                fields["rating"] = None
        elif key == "scraped_at" and isinstance(value, str):
            try:
                fields["scraped_at"] = datetime.fromisoformat(value)
            except ValueError:
                pass
        elif key in COMPANY_COLUMNS:
            fields[key] = value

    fields["task_id"] = task_id
    return Company(**fields)


def process_and_save(
    raw_dicts: list[dict],
    task_id: str,
    session,
    enrich: bool = False,
) -> tuple[int, int, int, list[StageResult]]:
    """Run pipeline on raw dicts, bulk insert Companies + PipelineStats.

    Returns (total_scraped, total_cleaned, total_deduped, stage_results).
    """
    stages = [HTMLCleaner(), FieldValidator(), Deduplicator()]
    if enrich:
        stages.append(Enricher())

    config = PipelineConfig(enrich=enrich)
    runner = PipelineRunner(stages=stages, config=config)
    processed_data, stage_results = runner.run(raw_dicts)

    total_scraped = stage_results[0].count_in if stage_results else len(raw_dicts)

    total_cleaned = total_scraped
    total_deduped = total_scraped
    for sr in stage_results:
        if "validator" in sr.stage_name.lower():
            total_cleaned = sr.count_out
        if "dedup" in sr.stage_name.lower():
            total_deduped = sr.count_out

    companies = [_map_dict_to_company(d, task_id) for d in processed_data]
    session.add_all(companies)
    session.flush()

    for sr in stage_results:
        stat = PipelineStat(
            task_id=task_id,
            stage=sr.stage_name,
            count_in=sr.count_in,
            count_out=sr.count_out,
            count_removed=sr.count_removed,
            count_modified=sr.count_modified,
            duration_ms=sr.duration_ms,
            details=sr.details if sr.details else None,
        )
        session.add(stat)

    session.commit()
    return total_scraped, total_cleaned, total_deduped, stage_results
