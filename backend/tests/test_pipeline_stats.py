import json
from pipeline.stats import PipelineStats


class TestPipelineStats:
    def test_accepts_valid_data(self):
        stats = PipelineStats(
            stage="html_cleaner", count_in=100, count_out=100,
            count_removed=0, count_modified=42, duration_ms=150,
        )
        assert stats.stage == "html_cleaner"
        assert stats.count_modified == 42

    def test_task_id_optional(self):
        stats = PipelineStats(
            stage="test", count_in=0, count_out=0,
            count_removed=0, count_modified=0, duration_ms=0,
        )
        assert stats.task_id is None

    def test_task_id_settable(self):
        stats = PipelineStats(
            task_id="abc-123", stage="test", count_in=0, count_out=0,
            count_removed=0, count_modified=0, duration_ms=0,
        )
        assert stats.task_id == "abc-123"

    def test_details_defaults_empty(self):
        stats = PipelineStats(
            stage="test", count_in=0, count_out=0,
            count_removed=0, count_modified=0, duration_ms=0,
        )
        assert stats.details == {}

    def test_details_accepts_nested(self):
        details = {"exact_phone_matches": 15, "total_duplicates": 31}
        stats = PipelineStats(
            stage="deduplicator", count_in=200, count_out=169,
            count_removed=31, count_modified=0, duration_ms=800,
            details=details,
        )
        assert stats.details["exact_phone_matches"] == 15

    def test_model_dump_json_serializable(self):
        stats = PipelineStats(
            task_id="xyz", stage="test", count_in=10, count_out=10,
            count_removed=0, count_modified=5, duration_ms=100,
            details={"key": "value"},
        )
        serialized = json.dumps(stats.model_dump())
        assert isinstance(serialized, str)
