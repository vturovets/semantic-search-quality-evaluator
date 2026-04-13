"""Abstract base class for the storage repository, mirroring the TypeScript StorageRepository interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

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


class StorageRepository(ABC):
    """Abstract storage interface matching the TypeScript StorageRepository."""

    # ── Imports ──────────────────────────────────────────────────────────

    @abstractmethod
    async def save_import(self, data: DatasetImport) -> None: ...

    @abstractmethod
    async def get_import(self, import_id: str) -> DatasetImport | None: ...

    # ── Raw imported records (pre-normalization) ─────────────────────────

    @abstractmethod
    async def save_imported_records(self, import_id: str, records: list[dict]) -> None: ...

    @abstractmethod
    async def get_imported_records(self, import_id: str) -> list[dict]: ...

    # ── Runs ─────────────────────────────────────────────────────────────

    @abstractmethod
    async def save_run(self, run: AnalysisRun) -> None: ...

    @abstractmethod
    async def get_run(self, run_id: str) -> AnalysisRun | None: ...

    @abstractmethod
    async def list_runs(self) -> list[AnalysisRun]: ...

    # ── Normalized records ───────────────────────────────────────────────

    @abstractmethod
    async def save_normalized_records(self, run_id: str, records: list[NormalizedRecord]) -> None: ...

    @abstractmethod
    async def get_normalized_records(self, run_id: str) -> list[NormalizedRecord]: ...

    # ── Canonical intents ────────────────────────────────────────────────

    @abstractmethod
    async def save_canonical_intents(self, run_id: str, intents: list[CanonicalIntent]) -> None: ...

    @abstractmethod
    async def get_canonical_intents(self, run_id: str) -> list[CanonicalIntent]: ...

    # ── Coverage metrics ─────────────────────────────────────────────────

    @abstractmethod
    async def save_coverage_metrics(self, run_id: str, metrics: list[IntentCoverageMetric]) -> None: ...

    @abstractmethod
    async def get_coverage_metrics(self, run_id: str) -> list[IntentCoverageMetric]: ...

    # ── Stability metrics ────────────────────────────────────────────────

    @abstractmethod
    async def save_stability_metrics(self, run_id: str, metrics: list[IntentShareStabilityMetric]) -> None: ...

    @abstractmethod
    async def get_stability_metrics(self, run_id: str) -> list[IntentShareStabilityMetric]: ...

    # ── Paraphrase metrics ───────────────────────────────────────────────

    @abstractmethod
    async def save_paraphrase_metrics(self, run_id: str, metrics: list[ParaphraseCoverageMetric]) -> None: ...

    @abstractmethod
    async def get_paraphrase_metrics(self, run_id: str) -> list[ParaphraseCoverageMetric]: ...

    # ── Recommendations ──────────────────────────────────────────────────

    @abstractmethod
    async def save_recommendations(self, run_id: str, recs: list[Recommendation]) -> None: ...

    @abstractmethod
    async def get_recommendations(
        self, run_id: str, filters: RecommendationFilters | None = None
    ) -> list[Recommendation]: ...

    @abstractmethod
    async def update_recommendation(self, id: str, update: dict) -> None: ...

    # ── Decisions ────────────────────────────────────────────────────────

    @abstractmethod
    async def save_decision(self, decision: RecommendationDecision) -> None: ...

    @abstractmethod
    async def get_decisions(self, recommendation_id: str) -> list[RecommendationDecision]: ...

    # ── Export artifacts ─────────────────────────────────────────────────

    @abstractmethod
    async def save_export_artifact(self, artifact: ExportArtifact) -> None: ...

    @abstractmethod
    async def get_export_artifacts(self, run_id: str) -> list[ExportArtifact]: ...
