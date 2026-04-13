"""Pydantic domain models matching lib/quality-evaluation/types.ts."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from models.enums import (
    ActionabilityClassification,
    DatasetType,
    ExportArtifactType,
    ExportFormat,
    IntentClassification,
    ObservationWindow,
    ParaphraseClassification,
    ProtectedClass,
    RecommendationPriority,
    RecommendationStatus,
    RecommendationType,
    RunStatus,
)


# ─── Audit Fields (DATA-2) ──────────────────────────────────────────────────


class AuditFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True, by_alias=True)

    id: str
    created_at: str = Field(alias="createdAt")
    created_by: str = Field(alias="createdBy")
    updated_at: str = Field(alias="updatedAt")
    version: int
    source_ref: str | None = Field(default=None, alias="sourceRef")


# ─── Confidence Interval ────────────────────────────────────────────────────


class ConfidenceInterval(BaseModel):
    model_config = ConfigDict(populate_by_name=True, by_alias=True)

    lower: float
    upper: float
    observed_share: float = Field(alias="observedShare")
    sample_size: int = Field(alias="sampleSize")
    confidence_level: float = Field(alias="confidenceLevel")
    method: Literal["wilson-score"]


# ─── Normalization Model (FR-5) ─────────────────────────────────────────────


class NormalizedRecord(AuditFields):
    original_source_id: str = Field(alias="originalSourceId")
    original_source_type: DatasetType = Field(alias="originalSourceType")
    original_values: dict[str, str] = Field(alias="originalValues")
    normalized_intent: str = Field(alias="normalizedIntent")
    normalized_status: str = Field(alias="normalizedStatus")
    normalized_options: list[str] = Field(alias="normalizedOptions")
    normalization_rule_id: str = Field(alias="normalizationRuleId")
    normalization_method: Literal["deterministic", "heuristic", "ai-assisted"] = Field(
        alias="normalizationMethod"
    )
    confidence: float | None = None
    explanation: str | None = None


# ─── Canonical Intent Model (FR-6) ─────────────────────────────────────────


class OutcomeSignature(BaseModel):
    model_config = ConfigDict(populate_by_name=True, by_alias=True)

    normalized_status: str = Field(alias="normalizedStatus")
    normalized_options: list[str] = Field(alias="normalizedOptions")
    rule_behavior_markers: list[str] = Field(alias="ruleBehaviorMarkers")
    protected_class_markers: list[ProtectedClass] = Field(alias="protectedClassMarkers")


class CanonicalIntent(AuditFields):
    intent_id: str = Field(alias="intentId")
    intent_label: str = Field(alias="intentLabel")
    intent_family: str = Field(alias="intentFamily")
    expected_business_meaning: str = Field(alias="expectedBusinessMeaning")
    expected_outcome_signature: OutcomeSignature = Field(alias="expectedOutcomeSignature")
    is_protected: bool = Field(alias="isProtected")
    protected_classes: list[ProtectedClass] = Field(alias="protectedClasses")
    related_business_requirements: list[str] = Field(alias="relatedBusinessRequirements")
    linked_accuracy_case_ids: list[str] = Field(alias="linkedAccuracyCaseIds")
    linked_consistency_group_ids: list[str] = Field(alias="linkedConsistencyGroupIds")
    linked_real_input_cluster_ids: list[str] = Field(alias="linkedRealInputClusterIds")


# ─── Coverage Metrics (FR-7) ───────────────────────────────────────────────


class IntentCoverageMetric(AuditFields):
    run_id: str = Field(alias="runId")
    intent_id: str = Field(alias="intentId")
    intent_label: str = Field(alias="intentLabel")
    intent_family: str = Field(alias="intentFamily")
    classification: IntentClassification
    real_input_count: int = Field(alias="realInputCount")
    real_input_share_percent: float = Field(alias="realInputSharePercent")
    golden_set_case_count: int = Field(alias="goldenSetCaseCount")
    golden_set_share_percent: float = Field(alias="goldenSetSharePercent")
    representation_delta: float = Field(alias="representationDelta")
    is_protected: bool = Field(alias="isProtected")
    protected_classes: list[ProtectedClass] = Field(alias="protectedClasses")
    is_recommendation_candidate: bool = Field(alias="isRecommendationCandidate")
    confidence_interval: ConfidenceInterval = Field(alias="confidenceInterval")
    actionability: ActionabilityClassification


# ─── Statistical Stability (FR-7.3) ────────────────────────────────────────


class IntentShareStabilityMetric(AuditFields):
    run_id: str = Field(alias="runId")
    intent_id: str = Field(alias="intentId")
    observed_count: int = Field(alias="observedCount")
    total_sample_size: int = Field(alias="totalSampleSize")
    observed_share: float = Field(alias="observedShare")
    confidence_interval: ConfidenceInterval = Field(alias="confidenceInterval")
    materiality_threshold: float = Field(alias="materialityThreshold")
    actionability: ActionabilityClassification
    meets_min_sample_size: bool = Field(alias="meetsMinSampleSize")
    rationale: str


# ─── Paraphrase Coverage (FR-8) ────────────────────────────────────────────


class ParaphraseCoverageMetric(AuditFields):
    run_id: str = Field(alias="runId")
    intent_id: str = Field(alias="intentId")
    paraphrase_group_id: str = Field(alias="paraphraseGroupId")
    classification: ParaphraseClassification
    golden_paraphrase_count: int = Field(alias="goldenParaphraseCount")
    real_wording_variant_count: int = Field(alias="realWordingVariantCount")
    uncovered_variants: list[str] = Field(alias="uncoveredVariants")
    is_protected: bool = Field(alias="isProtected")
    has_instability_signal: bool = Field(alias="hasInstabilitySignal")
    outcome_variability: list[str] = Field(alias="outcomeVariability")


# ─── Recommendation (FR-9) ─────────────────────────────────────────────────


class Recommendation(AuditFields):
    recommendation_id: str = Field(alias="recommendationId")
    run_id: str = Field(alias="runId")
    type: RecommendationType
    affected_golden_set: Literal["accuracy", "consistency", "both"] = Field(
        alias="affectedGoldenSet"
    )
    impacted_intent_id: str = Field(alias="impactedIntentId")
    impacted_intent_family: str = Field(alias="impactedIntentFamily")
    reason: str
    observed_frequency: int = Field(alias="observedFrequency")
    observed_share_percent: float = Field(alias="observedSharePercent")
    current_golden_representation: int = Field(alias="currentGoldenRepresentation")
    identified_gap: str = Field(alias="identifiedGap")
    proposed_action: str = Field(alias="proposedAction")
    priority: RecommendationPriority
    status: RecommendationStatus
    is_protected: bool = Field(alias="isProtected")
    protected_classes: list[ProtectedClass] = Field(alias="protectedClasses")
    actionability: ActionabilityClassification
    supporting_record_ids: list[str] = Field(alias="supportingRecordIds")
    supporting_cluster_ids: list[str] = Field(alias="supportingClusterIds")


# ─── Recommendation Decision / Approval (FR-12) ────────────────────────────


class RecommendationDecision(AuditFields):
    recommendation_id: str = Field(alias="recommendationId")
    from_status: RecommendationStatus = Field(alias="fromStatus")
    to_status: RecommendationStatus = Field(alias="toStatus")
    action: Literal["advance", "reject", "override"]
    reason: str | None = None
    decided_by: str = Field(alias="decidedBy")
    decided_at: str = Field(alias="decidedAt")
    requires_ba_qa_approval: bool = Field(alias="requiresBaQaApproval")
    ba_qa_approved: bool | None = Field(default=None, alias="baQaApproved")


# ─── Validation Issue ──────────────────────────────────────────────────────


class ValidationIssue(BaseModel):
    model_config = ConfigDict(populate_by_name=True, by_alias=True)

    row: int | None = None
    field: str | None = None
    severity: Literal["error", "warning"]
    message: str


# ─── Dataset Import (DATA-1) ───────────────────────────────────────────────


class DatasetImport(AuditFields):
    import_id: str = Field(alias="importId")
    dataset_type: DatasetType = Field(alias="datasetType")
    file_name: str = Field(alias="fileName")
    record_count: int = Field(alias="recordCount")
    validation_status: Literal["valid", "warnings", "rejected"] = Field(
        alias="validationStatus"
    )
    validation_issues: list[ValidationIssue] = Field(alias="validationIssues")
    parsed_at: str = Field(alias="parsedAt")


# ─── Protected Case Rule ───────────────────────────────────────────────────


class ProtectedCaseRule(BaseModel):
    model_config = ConfigDict(populate_by_name=True, by_alias=True)

    protected_class: ProtectedClass = Field(alias="protectedClass")
    description: str
    enabled: bool


# ─── Analysis Run (DATA-1) ─────────────────────────────────────────────────


class AnalysisRun(AuditFields):
    run_id: str = Field(alias="runId")
    name: str
    status: RunStatus
    observation_window: ObservationWindow = Field(alias="observationWindow")
    real_input_dataset_id: str = Field(alias="realInputDatasetId")
    accuracy_golden_set_id: str | None = Field(default=None, alias="accuracyGoldenSetId")
    consistency_golden_set_id: str | None = Field(default=None, alias="consistencyGoldenSetId")
    reference_catalog_ids: list[str] = Field(alias="referenceCatalogIds")
    materiality_threshold: float = Field(alias="materialityThreshold")
    min_sample_size: int = Field(alias="minSampleSize")
    confidence_level: float = Field(alias="confidenceLevel")
    protected_case_rules: list[ProtectedCaseRule] = Field(alias="protectedCaseRules")
    total_real_inputs: int = Field(alias="totalRealInputs")
    canonical_intent_count: int = Field(alias="canonicalIntentCount")
    recommendation_count: int = Field(alias="recommendationCount")
    completed_at: str | None = Field(default=None, alias="completedAt")


# ─── Export Artifact ────────────────────────────────────────────────────────


class ExportArtifact(AuditFields):
    export_id: str = Field(alias="exportId")
    run_id: str = Field(alias="runId")
    format: ExportFormat
    artifacts: list[ExportArtifactType]
    generated_at: str = Field(alias="generatedAt")
    pii_safe: bool = Field(alias="piiSafe")


# ─── Dashboard Summary (FR-14) ─────────────────────────────────────────────


class RunSummaryMetrics(BaseModel):
    model_config = ConfigDict(populate_by_name=True, by_alias=True)

    observation_window: ObservationWindow = Field(alias="observationWindow")
    real_inputs_analyzed: int = Field(alias="realInputsAnalyzed")
    canonical_intents_found: int = Field(alias="canonicalIntentsFound")
    accuracy_intents_covered: int = Field(alias="accuracyIntentsCovered")
    consistency_groups_reviewed: int = Field(alias="consistencyGroupsReviewed")
    real_only_intents: int = Field(alias="realOnlyIntents")
    golden_only_intents: int = Field(alias="goldenOnlyIntents")
    matched_intents: int = Field(alias="matchedIntents")
    underrepresented_intents: int = Field(alias="underrepresentedIntents")
    overrepresented_intents: int = Field(alias="overrepresentedIntents")
    candidate_obsolete_intents: int = Field(alias="candidateObsoleteIntents")
    action_ready_intents: int = Field(alias="actionReadyIntents")
    monitor_intents: int = Field(alias="monitorIntents")
    insufficient_evidence_intents: int = Field(alias="insufficientEvidenceIntents")
    narrow_paraphrase_groups: int = Field(alias="narrowParaphraseGroups")
    critical_recommendations: int = Field(alias="criticalRecommendations")
    protected_cases_retained: int = Field(alias="protectedCasesRetained")
    materiality_threshold: float = Field(alias="materialityThreshold")
    confidence_level: float = Field(alias="confidenceLevel")
    meets_min_sample_size: bool = Field(alias="meetsMinSampleSize")
