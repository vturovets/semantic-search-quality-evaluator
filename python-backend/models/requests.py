"""Pydantic request/response models matching lib/quality-evaluation/types.ts API types."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from models.domain import (
    AnalysisRun,
    IntentCoverageMetric,
    IntentShareStabilityMetric,
    ParaphraseCoverageMetric,
    ProtectedCaseRule,
    Recommendation,
    RunSummaryMetrics,
    ValidationIssue,
)
from models.enums import (
    DatasetType,
    ExportArtifactType,
    ExportFormat,
    ObservationWindow,
    RecommendationPriority,
    RecommendationStatus,
    RecommendationType,
    RunStatus,
)


# ─── POST /api/quality-evaluation/runs — Request ───────────────────────────


class CreateRunRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, by_alias=True)

    name: str = Field(min_length=1)
    observation_window: ObservationWindow = Field(alias="observationWindow")
    real_input_dataset_id: str = Field(alias="realInputDatasetId", min_length=1)
    accuracy_golden_set_id: str | None = Field(default=None, alias="accuracyGoldenSetId")
    consistency_golden_set_id: str | None = Field(default=None, alias="consistencyGoldenSetId")
    reference_catalog_ids: list[str] | None = Field(default=None, alias="referenceCatalogIds")
    materiality_threshold: float | None = Field(
        default=None, alias="materialityThreshold", ge=0, le=1
    )
    min_sample_size: int | None = Field(
        default=None, alias="minSampleSize", gt=0
    )
    confidence_level: float | None = Field(
        default=None, alias="confidenceLevel", gt=0, lt=1
    )
    protected_case_rules: list[ProtectedCaseRule] | None = Field(
        default=None, alias="protectedCaseRules"
    )


# ─── POST /api/quality-evaluation/runs — Response ──────────────────────────


class ValidationSummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True, by_alias=True)

    is_valid: bool = Field(alias="isValid")
    errors: list[str]
    warnings: list[str]


class CreateRunResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, by_alias=True)

    run_id: str = Field(alias="runId")
    status: RunStatus
    validation_summary: ValidationSummary = Field(alias="validationSummary")


# ─── POST /api/quality-evaluation/import — Request metadata ────────────────


class ImportMetadata(BaseModel):
    model_config = ConfigDict(populate_by_name=True, by_alias=True)

    dataset_type: DatasetType = Field(alias="datasetType")
    name: str = Field(min_length=1)
    version: str | None = None


# ─── POST /api/quality-evaluation/import — Response ────────────────────────


class ImportResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, by_alias=True)

    import_id: str = Field(alias="importId")
    record_count: int = Field(alias="recordCount")
    validation_issues: list[ValidationIssue] = Field(alias="validationIssues")
    status: Literal["valid", "warnings", "rejected"]


# ─── POST /api/quality-evaluation/normalize ─────────────────────────────────


class NormalizeRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, by_alias=True)

    run_id: str = Field(alias="runId", min_length=1)


class NormalizeResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, by_alias=True)

    canonical_intent_count: int = Field(alias="canonicalIntentCount")
    normalized_record_count: int = Field(alias="normalizedRecordCount")
    warnings: list[str]


# ─── POST /api/quality-evaluation/analyze ───────────────────────────────────


class AnalyzeRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, by_alias=True)

    run_id: str = Field(alias="runId", min_length=1)


class AnalyzeResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, by_alias=True)

    coverage_metrics: list[IntentCoverageMetric] = Field(alias="coverageMetrics")
    stability_metrics: list[IntentShareStabilityMetric] = Field(alias="stabilityMetrics")
    wording_metrics: list[ParaphraseCoverageMetric] = Field(alias="wordingMetrics")
    recommendation_count: int = Field(alias="recommendationCount")
    status: RunStatus


# ─── GET /api/quality-evaluation/runs/{runId} — Response ───────────────────


class RunDetailResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, by_alias=True)

    run: AnalysisRun
    summary_metrics: RunSummaryMetrics = Field(alias="summaryMetrics")
    recommendations: list[Recommendation]


# ─── GET /api/quality-evaluation/recommendations — Response ────────────────


class RecommendationListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, by_alias=True)

    items: list[Recommendation]
    total: int
    page: int
    page_size: int = Field(alias="pageSize")


# ─── PATCH /api/quality-evaluation/recommendations/{id} — Request ──────────


class UpdateRecommendationRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, by_alias=True)

    priority: RecommendationPriority | None = None
    rationale: str | None = None
    status: RecommendationStatus | None = None
    proposed_action: str | None = Field(default=None, alias="proposedAction")


# ─── POST /api/quality-evaluation/approvals — Request ──────────────────────


class ApprovalRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, by_alias=True)

    recommendation_id: str = Field(alias="recommendationId", min_length=1)
    action: Literal["approve", "reject"]
    reason: str | None = None
    approver_role: Literal["analyst", "ba_qa", "po"] = Field(alias="approverRole")


# ─── POST /api/quality-evaluation/exports — Request ────────────────────────


class ExportRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, by_alias=True)

    run_id: str = Field(alias="runId", min_length=1)
    format: ExportFormat
    artifacts: list[ExportArtifactType] = Field(min_length=1)


# ─── POST /api/quality-evaluation/exports — Response ───────────────────────


class ExportResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, by_alias=True)

    export_id: str = Field(alias="exportId")
    download_url: str = Field(alias="downloadUrl")
    format: ExportFormat


# ─── Recommendation Filters ────────────────────────────────────────────────


class RecommendationFilters(BaseModel):
    model_config = ConfigDict(populate_by_name=True, by_alias=True)

    type: RecommendationType | None = None
    priority: RecommendationPriority | None = None
    status: RecommendationStatus | None = None
    protected_flag: bool | None = Field(default=None, alias="protectedFlag")
    intent_family: str | None = Field(default=None, alias="intentFamily")
    golden_set: Literal["accuracy", "consistency", "both"] | None = Field(
        default=None, alias="goldenSet"
    )
    page: int | None = None
    page_size: int | None = Field(default=None, alias="pageSize")
