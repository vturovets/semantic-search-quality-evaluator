"""Property 22: Export Format Structure

For any export request, Markdown exports should contain sections for run summary,
coverage metrics, recommendations by priority, and protected cases. CSV exports
should have the correct column headers per artifact type. JSON exports should be
wrapped in an object with artifactType, exportedAt, recordCount, and data fields.

**Validates: Requirements 10.3, 10.4, 10.5**
"""

from __future__ import annotations

# Feature: python-analysis-backend, Property 22: Export Format Structure

import json as json_mod

from hypothesis import given, settings
from hypothesis import strategies as st

from engine.export import (
    export_markdown,
    export_csv,
    export_json,
    get_csv_headers,
)

# ─── Strategies ──────────────────────────────────────────────────────────────

_safe_text = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N")),
    min_size=1,
    max_size=20,
)

_priority = st.sampled_from(["critical", "high", "medium", "low"])


def _run():
    return st.fixed_dictionaries({
        "name": _safe_text,
        "runId": _safe_text,
        "status": st.sampled_from(["completed", "analyzing"]),
    })


def _metrics():
    return st.fixed_dictionaries({
        "observationWindow": st.sampled_from([7, 30, 90]),
        "realInputsAnalyzed": st.integers(min_value=0, max_value=10000),
        "canonicalIntentsFound": st.integers(min_value=0, max_value=100),
        "materialityThreshold": st.floats(min_value=0, max_value=1, allow_nan=False),
        "confidenceLevel": st.floats(min_value=0, max_value=1, allow_nan=False),
        "meetsMinSampleSize": st.booleans(),
        "matchedIntents": st.integers(min_value=0, max_value=50),
        "realOnlyIntents": st.integers(min_value=0, max_value=50),
        "goldenOnlyIntents": st.integers(min_value=0, max_value=50),
        "underrepresentedIntents": st.integers(min_value=0, max_value=50),
        "overrepresentedIntents": st.integers(min_value=0, max_value=50),
        "candidateObsoleteIntents": st.integers(min_value=0, max_value=50),
        "actionReadyIntents": st.integers(min_value=0, max_value=50),
        "monitorIntents": st.integers(min_value=0, max_value=50),
        "insufficientEvidenceIntents": st.integers(min_value=0, max_value=50),
        "accuracyIntentsCovered": st.integers(min_value=0, max_value=50),
        "consistencyGroupsReviewed": st.integers(min_value=0, max_value=50),
        "narrowParaphraseGroups": st.integers(min_value=0, max_value=50),
    })


def _recommendation():
    return st.fixed_dictionaries({
        "recommendationId": _safe_text,
        "runId": _safe_text,
        "type": st.sampled_from([
            "add-new-intent", "add-examples-for-intent", "no-update",
        ]),
        "affectedGoldenSet": st.just("accuracy"),
        "impactedIntentId": _safe_text,
        "impactedIntentFamily": _safe_text,
        "reason": _safe_text,
        "observedFrequency": st.integers(min_value=0, max_value=100),
        "observedSharePercent": st.floats(min_value=0, max_value=100, allow_nan=False),
        "currentGoldenRepresentation": st.integers(min_value=0, max_value=100),
        "identifiedGap": _safe_text,
        "proposedAction": _safe_text,
        "priority": _priority,
        "status": st.just("draft"),
        "isProtected": st.booleans(),
        "protectedClasses": st.lists(
            st.sampled_from(["policy-blocked", "pii-related"]),
            max_size=2,
        ),
        "actionability": st.just("action-ready"),
    })


_artifact_type = st.sampled_from([
    "recommendation-list", "intent-coverage-table", "wording-gap-table",
    "approval-register", "change-proposal",
])


# ─── Property Tests ─────────────────────────────────────────────────────────


@given(
    run=_run(),
    metrics=_metrics(),
    recs=st.lists(_recommendation(), min_size=0, max_size=5),
)
@settings(max_examples=100)
def test_markdown_contains_required_sections(run, metrics, recs):
    """Markdown export contains run summary, coverage metrics, recommendations by priority,
    and protected cases sections."""
    md = export_markdown(run, metrics, recs)

    assert "## Run Summary" in md
    assert "## Coverage Metrics" in md
    assert "## Recommendations by Priority" in md
    assert "## Protected Cases" in md


@given(
    run=_run(),
    metrics=_metrics(),
    recs=st.lists(_recommendation(), min_size=0, max_size=5),
)
@settings(max_examples=100)
def test_markdown_title_contains_run_name(run, metrics, recs):
    """Markdown export title contains the run name."""
    md = export_markdown(run, metrics, recs)
    assert f"# Quality Evaluation Report: {run['name']}" in md


@given(artifact_type=_artifact_type)
@settings(max_examples=100)
def test_csv_headers_match_artifact_type(artifact_type):
    """CSV export has the correct column headers per artifact type."""
    headers = get_csv_headers(artifact_type)
    assert len(headers) > 0, f"No headers for artifact type: {artifact_type}"

    # Generate empty CSV to check headers
    csv_output = export_csv([], artifact_type)
    header_line = csv_output.strip()
    expected_header = ",".join(headers)
    assert header_line == expected_header


@given(
    data=st.lists(_recommendation(), min_size=1, max_size=5),
)
@settings(max_examples=100)
def test_csv_has_correct_row_count(data):
    """CSV export has one header row plus one row per record."""
    csv_output = export_csv(data, "recommendation-list")
    lines = [l for l in csv_output.strip().split("\n") if l]
    # 1 header + N data rows
    assert len(lines) == 1 + len(data)


@given(
    data=st.lists(_recommendation(), min_size=0, max_size=5),
    artifact_type=_artifact_type,
)
@settings(max_examples=100)
def test_json_export_has_required_wrapper_fields(data, artifact_type):
    """JSON export is wrapped in an object with artifactType, exportedAt, recordCount, and data."""
    json_output = export_json(data, artifact_type)
    parsed = json_mod.loads(json_output)

    assert "artifactType" in parsed
    assert parsed["artifactType"] == artifact_type
    assert "exportedAt" in parsed
    assert "recordCount" in parsed
    assert parsed["recordCount"] == len(data)
    assert "data" in parsed
    assert isinstance(parsed["data"], list)


@given(
    data=st.lists(_recommendation(), min_size=1, max_size=5),
)
@settings(max_examples=100)
def test_json_export_record_count_matches_data(data):
    """JSON export recordCount matches the length of the data array."""
    json_output = export_json(data, "recommendation-list")
    parsed = json_mod.loads(json_output)

    assert parsed["recordCount"] == len(parsed["data"])
