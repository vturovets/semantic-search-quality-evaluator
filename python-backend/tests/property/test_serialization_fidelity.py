"""Property 25: Serialization Fidelity

For any domain entity serialized to JSON, enum/literal values should use the
same kebab-case string representations as the TypeScript types, all audit fields
should be present, and all datetime fields should be valid ISO 8601 strings.

**Validates: Requirements 14.2, 14.3, 14.4**
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from models.domain import (
    AnalysisRun,
    ConfidenceInterval,
    DatasetImport,
    ExportArtifact,
    IntentCoverageMetric,
    IntentShareStabilityMetric,
    NormalizedRecord,
    ParaphraseCoverageMetric,
    Recommendation,
    RecommendationDecision,
    ValidationIssue,
)
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


# ─── Helpers ─────────────────────────────────────────────────────────────────

ISO_8601_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
)

AUDIT_FIELDS = {"id", "createdAt", "createdBy", "updatedAt", "version"}

KEBAB_CASE_ENUMS = {
    "classification": [
        "matched", "real-only", "golden-only", "underrepresented",
        "overrepresented", "candidate-obsolete", "protected-retained",
        "adequately-represented", "narrow", "missing",
    ],
    "actionability": [
        "action-ready", "monitor", "insufficient-evidence", "protected-override",
    ],
    "type": [
        "add-new-intent", "add-examples-for-intent", "add-paraphrase-variants",
        "create-paraphrase-group", "add-unsupported-coverage",
        "add-policy-pii-coverage", "reduce-retire-obsolete", "no-update",
    ],
    "priority": ["critical", "high", "medium", "low"],
    "status": [
        "draft", "analyst-reviewed", "po-review-pending", "approved",
        "rejected", "implemented", "archived",
        "created", "importing", "normalizing", "analyzing", "completed", "failed",
        "valid", "warnings",
    ],
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ─── Strategies ──────────────────────────────────────────────────────────────

_nonempty = st.text(
    alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyz0123456789-"),
    min_size=1, max_size=20,
)

_iso_dt = st.just(_now_iso())

_ci = st.builds(
    ConfidenceInterval,
    lower=st.just(0.01),
    upper=st.just(0.05),
    observedShare=st.just(0.03),
    sampleSize=st.just(1000),
    confidenceLevel=st.just(0.95),
    method=st.just("wilson-score"),
)

_recommendation_st = st.builds(
    Recommendation,
    id=_nonempty,
    createdAt=_iso_dt,
    createdBy=st.just("system"),
    updatedAt=_iso_dt,
    version=st.just(1),
    recommendationId=_nonempty,
    runId=_nonempty,
    type=st.sampled_from(["add-new-intent", "add-examples-for-intent", "add-paraphrase-variants",
                           "create-paraphrase-group", "add-unsupported-coverage",
                           "add-policy-pii-coverage", "reduce-retire-obsolete", "no-update"]),
    affectedGoldenSet=st.sampled_from(["accuracy", "consistency", "both"]),
    impactedIntentId=_nonempty,
    impactedIntentFamily=_nonempty,
    reason=_nonempty,
    observedFrequency=st.integers(min_value=0, max_value=10000),
    observedSharePercent=st.floats(min_value=0, max_value=100),
    currentGoldenRepresentation=st.integers(min_value=0, max_value=1000),
    identifiedGap=_nonempty,
    proposedAction=_nonempty,
    priority=st.sampled_from(["critical", "high", "medium", "low"]),
    status=st.sampled_from(["draft", "analyst-reviewed", "po-review-pending",
                             "approved", "rejected", "implemented", "archived"]),
    isProtected=st.booleans(),
    protectedClasses=st.just([]),
    actionability=st.sampled_from(["action-ready", "monitor", "insufficient-evidence", "protected-override"]),
    supportingRecordIds=st.just([]),
    supportingClusterIds=st.just([]),
)

_analysis_run_st = st.builds(
    AnalysisRun,
    id=_nonempty,
    createdAt=_iso_dt,
    createdBy=st.just("system"),
    updatedAt=_iso_dt,
    version=st.just(1),
    runId=_nonempty,
    name=_nonempty,
    status=st.sampled_from(["created", "importing", "normalizing", "analyzing", "completed", "failed"]),
    observationWindow=st.sampled_from([7, 30, 90]),
    realInputDatasetId=_nonempty,
    accuracyGoldenSetId=_nonempty,
    consistencyGoldenSetId=_nonempty,
    referenceCatalogIds=st.just([]),
    materialityThreshold=st.floats(min_value=0.001, max_value=0.1),
    minSampleSize=st.integers(min_value=10, max_value=10000),
    confidenceLevel=st.floats(min_value=0.8, max_value=0.99),
    protectedCaseRules=st.just([]),
    totalRealInputs=st.integers(min_value=0, max_value=100000),
    canonicalIntentCount=st.integers(min_value=0, max_value=1000),
    recommendationCount=st.integers(min_value=0, max_value=1000),
)


# ─── Property Tests ─────────────────────────────────────────────────────────
# Feature: python-analysis-backend, Property 25: Serialization Fidelity


@given(rec=_recommendation_st)
@settings(max_examples=100)
def test_recommendation_serialization_fidelity(rec: Recommendation):
    """Recommendation serialized to JSON has correct audit fields, kebab-case enums, and ISO dates."""
    data = rec.model_dump(by_alias=True)

    # All audit fields present
    for field in AUDIT_FIELDS:
        assert field in data, f"Missing audit field: {field}"

    # Datetime fields are valid ISO 8601
    assert ISO_8601_PATTERN.match(data["createdAt"]), f"Invalid ISO date: {data['createdAt']}"
    assert ISO_8601_PATTERN.match(data["updatedAt"]), f"Invalid ISO date: {data['updatedAt']}"

    # Enum fields use kebab-case
    assert data["type"] in KEBAB_CASE_ENUMS["type"], f"Invalid type: {data['type']}"
    assert data["priority"] in KEBAB_CASE_ENUMS["priority"], f"Invalid priority: {data['priority']}"
    assert data["status"] in KEBAB_CASE_ENUMS["status"], f"Invalid status: {data['status']}"
    assert data["actionability"] in KEBAB_CASE_ENUMS["actionability"], f"Invalid actionability: {data['actionability']}"


@given(run=_analysis_run_st)
@settings(max_examples=100)
def test_analysis_run_serialization_fidelity(run: AnalysisRun):
    """AnalysisRun serialized to JSON has correct audit fields, kebab-case enums, and ISO dates."""
    data = run.model_dump(by_alias=True)

    # All audit fields present
    for field in AUDIT_FIELDS:
        assert field in data, f"Missing audit field: {field}"

    # Datetime fields are valid ISO 8601
    assert ISO_8601_PATTERN.match(data["createdAt"])
    assert ISO_8601_PATTERN.match(data["updatedAt"])

    # Status uses kebab-case
    assert data["status"] in KEBAB_CASE_ENUMS["status"], f"Invalid status: {data['status']}"

    # observationWindow is one of the valid values
    assert data["observationWindow"] in [7, 30, 90]

    # camelCase aliases are used
    assert "runId" in data
    assert "observationWindow" in data
    assert "materialityThreshold" in data
    assert "minSampleSize" in data
    assert "confidenceLevel" in data


@given(rec=_recommendation_st)
@settings(max_examples=100)
def test_recommendation_camel_case_aliases(rec: Recommendation):
    """Recommendation JSON uses camelCase aliases matching TypeScript API contracts."""
    data = rec.model_dump(by_alias=True)

    expected_camel_keys = [
        "recommendationId", "runId", "affectedGoldenSet",
        "impactedIntentId", "impactedIntentFamily",
        "observedFrequency", "observedSharePercent",
        "currentGoldenRepresentation", "identifiedGap",
        "proposedAction", "isProtected", "protectedClasses",
        "supportingRecordIds", "supportingClusterIds",
    ]
    for key in expected_camel_keys:
        assert key in data, f"Missing camelCase key: {key}"

    # snake_case keys should NOT be present
    snake_keys = [
        "recommendation_id", "run_id", "affected_golden_set",
        "impacted_intent_id", "impacted_intent_family",
        "observed_frequency", "observed_share_percent",
        "current_golden_representation", "identified_gap",
        "proposed_action", "is_protected", "protected_classes",
        "supporting_record_ids", "supporting_cluster_ids",
    ]
    for key in snake_keys:
        assert key not in data, f"Unexpected snake_case key: {key}"
