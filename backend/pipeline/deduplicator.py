from __future__ import annotations

import re
from collections import defaultdict

import numpy as np
from rapidfuzz import fuzz, process

from pipeline.base import PipelineStage

_PREFIX_RE = re.compile(r"^(the|a|an)\s+", re.IGNORECASE)


class Deduplicator(PipelineStage):
    def __init__(
        self,
        auto_merge_threshold: int = 90,
        review_threshold: int = 85,
        scorer: str = "token_set_ratio",
    ) -> None:
        self._auto_threshold = auto_merge_threshold
        self._review_threshold = review_threshold
        self._scorer = getattr(fuzz, scorer)
        self._stats: dict = {}

    @property
    def name(self) -> str:
        return "deduplicator"

    def process(self, data: list[dict]) -> list[dict]:
        stats = {"exact_phone_matches": 0, "exact_email_matches": 0,
                 "fuzzy_auto_merged": 0, "fuzzy_flagged_review": 0, "total_duplicates": 0}

        removed_ids: set[str] = set()

        # Pass 1: Exact phone match
        self._exact_match(data, "phone_normalized", removed_ids, stats, "exact_phone_matches")

        # Pass 2: Exact email match
        self._exact_match(data, "email", removed_ids, stats, "exact_email_matches")

        # Pass 3: Fuzzy name match
        remaining = [r for r in data if r.get("_pipeline_id") not in removed_ids]
        self._fuzzy_match(remaining, removed_ids, stats)

        stats["total_duplicates"] = (
            stats["exact_phone_matches"] + stats["exact_email_matches"] +
            stats["fuzzy_auto_merged"] + stats["fuzzy_flagged_review"]
        )
        self._stats = stats

        return [r for r in data if r.get("_pipeline_id") not in removed_ids]

    def run(self, data, **kw):
        result_data, stage_result = super().run(data)
        stage_result.details = self._stats
        return result_data, stage_result

    def _exact_match(self, data: list[dict], field: str, removed_ids: set, stats: dict, stat_key: str):
        groups: dict[str, list[dict]] = defaultdict(list)
        for record in data:
            if record.get("_pipeline_id") in removed_ids:
                continue
            val = record.get(field)
            if val:
                groups[val].append(record)

        for key, group in groups.items():
            if len(group) < 2:
                continue
            primary = max(group, key=lambda r: sum(1 for v in r.values() if v is not None))
            for secondary in group:
                if secondary is primary:
                    continue
                self._merge_into(primary, secondary)
                secondary["is_duplicate_of"] = primary.get("_pipeline_id")
                removed_ids.add(secondary["_pipeline_id"])
                stats[stat_key] += 1

    def _fuzzy_match(self, data: list[dict], removed_ids: set, stats: dict):
        blocks: dict[str, list[dict]] = defaultdict(list)
        for record in data:
            if record.get("_pipeline_id") in removed_ids:
                continue
            name = record.get("company_name_normalized", "")
            if not name:
                continue
            clean = _PREFIX_RE.sub("", name).strip()
            block_key = clean[0] if clean else "_"
            blocks[block_key].append(record)

        for block_key, group in blocks.items():
            if len(group) < 2:
                continue
            names = [r.get("company_name_normalized", "") for r in group]
            matrix = process.cdist(
                names, names, scorer=self._scorer,
                score_cutoff=self._review_threshold, workers=-1,
                dtype=np.uint8,
            )
            matched: set[int] = set()
            for i in range(len(group)):
                if i in matched:
                    continue
                for j in range(i + 1, len(group)):
                    if j in matched:
                        continue
                    score = matrix[i][j]
                    if score >= self._auto_threshold:
                        primary, secondary = group[i], group[j]
                        self._merge_into(primary, secondary)
                        secondary["is_duplicate_of"] = primary.get("_pipeline_id")
                        removed_ids.add(secondary["_pipeline_id"])
                        matched.add(j)
                        stats["fuzzy_auto_merged"] += 1
                    elif score >= self._review_threshold:
                        group[j]["is_duplicate_of"] = group[i].get("_pipeline_id")
                        group[j]["needs_review"] = True
                        stats["fuzzy_flagged_review"] += 1

    @staticmethod
    def _merge_into(primary: dict, secondary: dict) -> None:
        for key, value in secondary.items():
            if key.startswith("_") or key in ("is_duplicate_of", "needs_review"):
                continue
            if primary.get(key) is None and value is not None:
                primary[key] = value
        # Keep longest company name
        p_name = primary.get("company_name", "")
        s_name = secondary.get("company_name", "")
        if len(s_name) > len(p_name):
            primary["company_name"] = s_name
