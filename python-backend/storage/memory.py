"""In-memory storage implementation using dicts, mirroring the TypeScript InMemoryStorage."""

from __future__ import annotations

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


def apply_recommendation_filters(
    recs: list[Recommendation],
    filters: RecommendationFilters | None,
) -> list[Recommendation]:
    """Filter recommendations matching the TypeScript applyRecommendationFilters logic."""
    if filters is None:
        return recs
    result = recs
    if filters.type is not None:
        result = [r for r in result if r.type == filters.type]
    if filters.priority is not None:
        result = [r for r in result if r.priority == filters.priority]
    if filters.status is not None:
        result = [r for r in result if r.status == filters.status]
    if filters.protected_flag is not None:
        result = [r for r in result if r.is_protected == filters.protected_flag]
    if filters.intent_family is not None:
        result = [r for r in result if r.impacted_intent_family == filters.intent_family]
    if filters.golden_set is not None:
        result = [r for r in result if r.affected_golden_set == filters.golden_set]
    return result


class InMemoryStorage(StorageRepository):
    """Dict-based in-memory storage for development and testing."""

    def __init__(self) -> None:
        self._imports: dict[str, DatasetImport] = {}
        self._imported_records: dict[str, list[dict]] = {}
        self._runs: dict[str, AnalysisRun] = {}
        self._normalized_records: dict[str, list[NormalizedRecord]] = {}
        self._canonical_intents: dict[str, list[CanonicalIntent]] = {}
        self._coverage_metrics: dict[str, list[IntentCoverageMetric]] = {}
        self._stability_metrics: dict[str, list[IntentShareStabilityMetric]] = {}
        self._paraphrase_metrics: dict[str, list[ParaphraseCoverageMetric]] = {}
        self._recommendations: dict[str, list[Recommendation]] = {}
        self._decisions: dict[str, list[RecommendationDecision]] = {}
        self._export_artifacts: dict[str, list[ExportArtifact]] = {}

    # ── Imports ──────────────────────────────────────────────────────────

    async def save_import(self, data: DatasetImport) -> None:
        self._imports[data.import_id] = data

    async def get_import(self, import_id: str) -> DatasetImport | None:
        return self._imports.get(import_id)

    # ── Raw imported records ─────────────────────────────────────────────

    async def save_imported_records(self, import_id: str, records: list[dict]) -> None:
        self._imported_records[import_id] = records

    async def get_imported_records(self, import_id: str) -> list[dict]:
        return self._imported_records.get(import_id, [])

    # ── Runs ─────────────────────────────────────────────────────────────

    async def save_run(self, run: AnalysisRun) -> None:
        self._runs[run.run_id] = run

    async def get_run(self, run_id: str) -> AnalysisRun | None:
        return self._runs.get(run_id)

    async def list_runs(self) -> list[AnalysisRun]:
        return list(self._runs.values())

    # ── Normalized records ───────────────────────────────────────────────

    async def save_normalized_records(self, run_id: str, records: list[NormalizedRecord]) -> None:
        self._normalized_records[run_id] = records

    async def get_normalized_records(self, run_id: str) -> list[NormalizedRecord]:
        return self._normalized_records.get(run_id, [])

    # ── Canonical intents ────────────────────────────────────────────────

    async def save_canonical_intents(self, run_id: str, intents: list[CanonicalIntent]) -> None:
        self._canonical_intents[run_id] = intents

    async def get_canonical_intents(self, run_id: str) -> list[CanonicalIntent]:
        return self._canonical_intents.get(run_id, [])

    # ── Coverage metrics ─────────────────────────────────────────────────

    async def save_coverage_metrics(self, run_id: str, metrics: list[IntentCoverageMetric]) -> None:
        self._coverage_metrics[run_id] = metrics

    async def get_coverage_metrics(self, run_id: str) -> list[IntentCoverageMetric]:
        return self._coverage_metrics.get(run_id, [])

    # ── Stability metrics ────────────────────────────────────────────────

    async def save_stability_metrics(self, run_id: str, metrics: list[IntentShareStabilityMetric]) -> None:
        self._stability_metrics[run_id] = metrics

    async def get_stability_metrics(self, run_id: str) -> list[IntentShareStabilityMetric]:
        return self._stability_metrics.get(run_id, [])

    # ── Paraphrase metrics ───────────────────────────────────────────────

    async def save_paraphrase_metrics(self, run_id: str, metrics: list[ParaphraseCoverageMetric]) -> None:
        self._paraphrase_metrics[run_id] = metrics

    async def get_paraphrase_metrics(self, run_id: str) -> list[ParaphraseCoverageMetric]:
        return self._paraphrase_metrics.get(run_id, [])

    # ── Recommendations ──────────────────────────────────────────────────

    async def save_recommendations(self, run_id: str, recs: list[Recommendation]) -> None:
        self._recommendations[run_id] = recs

    async def get_recommendations(
        self, run_id: str, filters: RecommendationFilters | None = None
    ) -> list[Recommendation]:
        recs = self._recommendations.get(run_id, [])
        return apply_recommendation_filters(recs, filters)

    async def update_recommendation(self, id: str, update: dict) -> None:
        for run_id, recs in self._recommendations.items():
            for i, r in enumerate(recs):
                if r.recommendation_id == id:
                    updated = r.model_copy(update=update)
                    recs[i] = updated
                    return

    # ── Decisions ────────────────────────────────────────────────────────

    async def save_decision(self, decision: RecommendationDecision) -> None:
        existing = self._decisions.get(decision.recommendation_id, [])
        existing.append(decision)
        self._decisions[decision.recommendation_id] = existing

    async def get_decisions(self, recommendation_id: str) -> list[RecommendationDecision]:
        return self._decisions.get(recommendation_id, [])

    # ── Export artifacts ─────────────────────────────────────────────────

    async def save_export_artifact(self, artifact: ExportArtifact) -> None:
        existing = self._export_artifacts.get(artifact.run_id, [])
        existing.append(artifact)
        self._export_artifacts[artifact.run_id] = existing

    async def get_export_artifacts(self, run_id: str) -> list[ExportArtifact]:
        return self._export_artifacts.get(run_id, [])
