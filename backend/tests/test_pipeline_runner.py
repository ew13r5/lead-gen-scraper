import pytest

from pipeline.base import PipelineConfig, PipelineRunner, PipelineStage, StageResult


class IncrementStage(PipelineStage):
    @property
    def name(self) -> str:
        return "increment"

    def process(self, data: list[dict]) -> list[dict]:
        for record in data:
            record["count"] = record.get("count", 0) + 1
        return data


class FilterStage(PipelineStage):
    @property
    def name(self) -> str:
        return "filter"

    def process(self, data: list[dict]) -> list[dict]:
        return [r for r in data if r.get("keep")]


class ErrorStage(PipelineStage):
    @property
    def name(self) -> str:
        return "error"

    def process(self, data: list[dict]) -> list[dict]:
        raise ValueError("Stage failed")


def make_records(n=3, **extra):
    return [{"company_name": f"Company {i}", "source": "test", **extra} for i in range(n)]


class TestPipelineStage:
    def test_abc_requires_process(self):
        with pytest.raises(TypeError):
            PipelineStage()

    def test_run_returns_tuple(self):
        stage = IncrementStage()
        data, result = stage.run(make_records())
        assert isinstance(data, list)
        assert isinstance(result, StageResult)

    def test_stage_result_counts(self):
        stage = FilterStage()
        records = make_records(3)
        records[0]["keep"] = True
        records[1]["keep"] = True
        for r in records:
            r["_pipeline_id"] = f"id-{records.index(r)}"
        data, result = stage.run(records)
        assert result.count_in == 3
        assert result.count_out == 2
        assert result.count_removed == 1

    def test_duration_positive(self):
        stage = IncrementStage()
        _, result = stage.run(make_records())
        assert result.duration_ms >= 0

    def test_count_modified(self):
        stage = IncrementStage()
        records = make_records(3)
        for i, r in enumerate(records):
            r["_pipeline_id"] = f"id-{i}"
        _, result = stage.run(records)
        assert result.count_modified == 3


class TestPipelineRunner:
    def test_chains_stages(self):
        records = make_records(4)
        records[0]["keep"] = True
        records[1]["keep"] = True
        runner = PipelineRunner([IncrementStage(), FilterStage()])
        data, results = runner.run(records)
        assert len(data) == 2
        assert len(results) == 2

    def test_handles_exception(self):
        runner = PipelineRunner([IncrementStage(), ErrorStage(), FilterStage()])
        data, results = runner.run(make_records())
        assert any(r.error for r in results)

    def test_returns_all_results_on_error(self):
        runner = PipelineRunner([IncrementStage(), ErrorStage()])
        _, results = runner.run(make_records())
        assert len(results) == 2
        assert results[0].error is None
        assert results[1].error is not None

    def test_empty_data(self):
        runner = PipelineRunner([IncrementStage()])
        data, results = runner.run([])
        assert data == []
        assert results[0].count_in == 0

    def test_assigns_pipeline_id(self):
        runner = PipelineRunner([IncrementStage()])
        records = make_records(2)
        data, _ = runner.run(records)
        for r in data:
            assert "_pipeline_id" in r

    def test_preserves_existing_pipeline_id(self):
        runner = PipelineRunner([IncrementStage()])
        records = make_records(1)
        records[0]["_pipeline_id"] = "custom-id"
        data, _ = runner.run(records)
        assert data[0]["_pipeline_id"] == "custom-id"

    def test_skips_missing_company_name(self):
        runner = PipelineRunner([IncrementStage()])
        records = [
            {"company_name": "Good", "source": "t"},
            {"source": "t"},  # no company_name
            {"company_name": None, "source": "t"},
        ]
        data, _ = runner.run(records)
        assert len(data) == 1

    def test_skip_stages(self):
        config = PipelineConfig(skip_stages=["increment"])
        runner = PipelineRunner([IncrementStage(), FilterStage()], config=config)
        records = make_records(2)
        records[0]["keep"] = True
        data, results = runner.run(records)
        assert len(results) == 1  # only filter ran
        assert "count" not in data[0]  # increment was skipped

    def test_coerces_int_phone(self):
        runner = PipelineRunner([IncrementStage()])
        records = [{"company_name": "Test", "phone": 5551234567}]
        data, _ = runner.run(records)
        assert data[0]["phone"] == "5551234567"
