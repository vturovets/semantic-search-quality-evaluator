"""File-backed JSON storage implementation, mirroring the TypeScript FileBackedStorage."""

from __future__ import annotations

import json
import os
from typing import Any, TypeVar

from pydantic import BaseModel

from models.domain import (
    AnalysisRun,
    CanonicalIntent,
    DatasetImport,
    ExportArtifact,
    IntentCoverageMetric,
    IntentShareStabilityMetric,
    NormalizedRecord,
    ParaphraseCoverageMetric,
    Recommendation,
    RecommendationDecision,
)
from models.requests import RecommendationFilters
from storage.base import StorageRepository
from storage.memory import apply_recommendation_filters

T = TypeVar("T", bound=BaseModel)


class FileBackedStorage(StorageRepository):
    """JSON file persistence storage mirroring the TypeScript FileBackedStorage."""

    def __init__(self, base_path: str) -> None:
        self._base_path = base_path
        os.makedirs(base_path, exist_ok=True)

    def _file_path(self, name: str) -> str:
        return os.path.join(self._base_path, f"{name}.json")

    def _read_json(self, name: str) -> Any:
        fp = self._file_path(name)
        if not os.path.exists(fp):
            return None
        with open(fp, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_json(self, name: str, data: Any) -> None:
        with open(self._file_path(name), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _read_map(self, name: str) -> dict[str, Any]:
        return self._read_json(name) or {}

    def _write_map(self, name: str, map_data: dict[str, Any]) -> None:
        self._write_json(name, map_data)

    # ── Imports ──────────────────────────────────────────────────────────

    async def save_import(self, data: DatasetImport) -> None:
        m = self._read_map("imports")
        m[data.import_id] = data.model_dump(by_alias=True)
        self._write_map("imports", m)

    async def get_import(self, import_id: str) -> DatasetImport | None:
        m = self._read_map("imports")
        raw = m.get(import_id)
        return DatasetImport.model_validate(raw) if raw else None

    # ── Raw imported records ─────────────────────────────────────────────

    async def save_imported_records(self, import_id: str, records: list[dict]) -> None:
        self._write_json(f"imported-records-{import_id}", records)

    async def get_imported_records(self, import_id: str) -> list[dict]:
        return self._read_json(f"imported-records-{import_id}") or []

    # ── Runs ─────────────────────────────────────────────────────────────

    async def save_run(self, run: AnalysisRun) -> None:
        m = self._read_map("runs")
        m[run.run_id] = run.model_dump(by_alias=True)
        self._write_map("runs", m)

    async def get_run(self, run_id: str) -> AnalysisRun | None:
        m = self._read_map("runs")
        raw = m.get(run_id)
        return AnalysisRun.model_validate(raw) if raw else None

    async def list_runs(self) -> list[AnalysisRun]:
        m = self._read_map("runs")
        return [AnalysisRun.model_validate(v) for v in m.values()]

    # ── Normalized records ───────────────────────────────────────────────

    async def save_normalized_records(self, run_id: str, records: list[NormalizedRecord]) -> None:
        m = self._read_map("normalized-records")
        m[run_id] = [r.model_dump(by_alias=True) for r in records]
        self._write_map("normalized-records", m)

    async def get_normalized_records(self, run_id: str) -> list[NormalizedRecord]:
        m = self._read_map("normalized-records")
        raw = m.get(run_id, [])
        return [NormalizedRecord.model_validate(r) for r in raw]

    # ── Canonical intents ────────────────────────────────────────────────

    async def save_canonical_intents(self, run_id: str, intents: list[CanonicalIntent]) -> None:
        m = self._read_map("canonical-intents")
        m[run_id] = [i.model_dump(by_alias=True) for i in intents]
        self._write_map("canonical-intents", m)

    async def get_canonical_intents(self, run_id: str) -> list[CanonicalIntent]:
        m = self._read_map("canonical-intents")
        raw = m.get(run_id, [])
        return [CanonicalIntent.model_validate(i) for i in raw]

    # ── Coverage metrics ─────────────────────────────────────────────────

    async def save_coverage_metrics(self, run_id: str, metrics: list[IntentCoverageMetric]) -> None:
        m = self._read_map("coverage-metrics")
        m[run_id] = [met.model_dump(by_alias=True) for met in metrics]
        self._write_map("coverage-metrics", m)

    async def get_coverage_metrics(self, run_id: str) -> list[IntentCoverageMetric]:
        m = self._read_map("coverage-metrics")
        raw = m.get(run_id, [])
        return [IntentCoverageMetric.model_validate(met) for met in raw]

    # ── Stability metrics ────────────────────────────────────────────────

    async def save_stability_metrics(self, run_id: str, metrics: list[IntentShareStabilityMetric]) -> None:
        m = self._read_map("stability-metrics")
        m[run_id] = [met.model_dump(by_alias=True) for met in metrics]
        self._write_map("stability-metrics", m)

    async def get_stability_metrics(self, run_id: str) -> list[IntentShareStabilityMetric]:
        m = self._read_map("stability-metrics")
        raw = m.get(run_id, [])
        return [IntentShareStabilityMetric.model_validate(met) for met in raw]

    # ── Paraphrase metrics ───────────────────────────────────────────────

    async def save_paraphrase_metrics(self, run_id: str, metrics: list[ParaphraseCoverageMetric]) -> None:
        m = self._read_map("paraphrase-metrics")
        m[run_id] = [met.model_dump(by_alias=True) for met in metrics]
        self._write_map("paraphrase-metrics", m)

    async def get_paraphrase_metrics(self, run_id: str) -> list[ParaphraseCoverageMetric]:
        m = self._read_map("paraphrase-metrics")
        raw = m.get(run_id, [])
        return [ParaphraseCoverageMetric.model_validate(met) for met in raw]

    # ── Recommendations ──────────────────────────────────────────────────

    async def save_recommendations(self, run_id: str, recs: list[Recommendation]) -> None:
        m = self._read_map("recommendations")
        m[run_id] = [r.model_dump(by_alias=True) for r in recs]
        self._write_map("recommendations", m)

    async def get_recommendations(
        self, run_id: str, filters: RecommendationFilters | None = None
    ) -> list[Recommendation]:
        m = self._read_map("recommendations")
        raw = m.get(run_id, [])
        recs = [Recommendation.model_validate(r) for r in raw]
        return apply_recommendation_filters(recs, filters)

    async def update_recommendation(self, id: str, update: dict) -> None:
        m = self._read_map("recommendations")
        for run_id, raw_recs in m.items():
            for i, raw in enumerate(raw_recs):
                rec = Recommendation.model_validate(raw)
                if rec.recommendation_id == id:
                    updated = rec.model_copy(update=update)
                    raw_recs[i] = updated.model_dump(by_alias=True)
                    m[run_id] = raw_recs
                    self._write_map("recommendations", m)
                    return

    # ── Decisions ────────────────────────────────────────────────────────

    async def save_decision(self, decision: RecommendationDecision) -> None:
        m = self._read_map("decisions")
        existing = m.get(decision.recommendation_id, [])
        existing.append(decision.model_dump(by_alias=True))
        m[decision.recommendation_id] = existing
        self._write_map("decisions", m)

    async def get_decisions(self, recommendation_id: str) -> list[RecommendationDecision]:
        m = self._read_map("decisions")
        raw = m.get(recommendation_id, [])
        return [RecommendationDecision.model_validate(d) for d in raw]

    # ── Export artifacts ─────────────────────────────────────────────────

    async def save_export_artifact(self, artifact: ExportArtifact) -> None:
        m = self._read_map("export-artifacts")
        existing = m.get(artifact.run_id, [])
        existing.append(artifact.model_dump(by_alias=True))
        m[artifact.run_id] = existing
        self._write_map("export-artifacts", m)

    async def get_export_artifacts(self, run_id: str) -> list[ExportArtifact]:
        m = self._read_map("export-artifacts")
        raw = m.get(run_id, [])
        return [ExportArtifact.model_validate(a) for a in raw]
