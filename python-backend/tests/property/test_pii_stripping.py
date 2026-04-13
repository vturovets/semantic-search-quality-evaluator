"""Property 21: PII Stripping in Exports

For any export output (Markdown, CSV, or JSON), the fields sanitizedText,
freeTextInput, and originalValues should never appear in the exported content.

**Validates: Requirements 10.2**
"""

from __future__ import annotations

# Feature: python-analysis-backend, Property 21: PII Stripping in Exports

from hypothesis import given, settings
from hypothesis import strategies as st

from engine.export import PII_FIELDS, strip_pii, export_csv, export_json

# ─── Strategies ──────────────────────────────────────────────────────────────

_safe_text = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N", "P", "Z")),
    min_size=0,
    max_size=30,
)


def _record_with_pii():
    """Generate a record that may contain PII fields."""
    return st.fixed_dictionaries({
        "recommendationId": _safe_text,
        "runId": st.just("run-1"),
        "type": st.just("add-new-intent"),
        "affectedGoldenSet": st.just("accuracy"),
        "impactedIntentId": _safe_text,
        "impactedIntentFamily": _safe_text,
        "reason": _safe_text,
        "observedFrequency": st.integers(min_value=0, max_value=100),
        "observedSharePercent": st.floats(min_value=0, max_value=100, allow_nan=False),
        "currentGoldenRepresentation": st.integers(min_value=0, max_value=100),
        "identifiedGap": _safe_text,
        "proposedAction": _safe_text,
        "priority": st.sampled_from(["critical", "high", "medium", "low"]),
        "status": st.just("draft"),
        "isProtected": st.booleans(),
        "protectedClasses": st.just([]),
        "actionability": st.just("action-ready"),
        # PII fields
        "sanitizedText": _safe_text,
        "freeTextInput": _safe_text,
        "originalValues": st.fixed_dictionaries({
            "query": _safe_text,
            "sanitizedText": _safe_text,
        }),
    })


# ─── Property Tests ─────────────────────────────────────────────────────────


@given(data=st.lists(_record_with_pii(), min_size=1, max_size=5))
@settings(max_examples=100)
def test_strip_pii_removes_all_pii_fields(data):
    """stripPII removes all PII-sensitive fields from records."""
    result = strip_pii(data)

    for record in result:
        for pii_field in PII_FIELDS:
            assert pii_field not in record, f"PII field '{pii_field}' not stripped"


@given(data=st.lists(_record_with_pii(), min_size=1, max_size=5))
@settings(max_examples=100)
def test_strip_pii_preserves_non_pii_fields(data):
    """stripPII preserves all non-PII fields."""
    result = strip_pii(data)

    for original, stripped in zip(data, result):
        for key in original:
            if key not in PII_FIELDS:
                assert key in stripped, f"Non-PII field '{key}' was removed"


@given(data=st.lists(_record_with_pii(), min_size=1, max_size=3))
@settings(max_examples=100)
def test_csv_export_contains_no_pii_field_names(data):
    """CSV export output does not contain PII field names as column headers."""
    csv_output = export_csv(data, "recommendation-list")

    # The header line should not contain PII field names
    header_line = csv_output.split("\n")[0]
    for pii_field in PII_FIELDS:
        assert pii_field not in header_line, f"PII field '{pii_field}' in CSV headers"


@given(data=st.lists(_record_with_pii(), min_size=1, max_size=3))
@settings(max_examples=100)
def test_json_export_contains_no_pii_fields(data):
    """JSON export output does not contain PII field keys."""
    import json as json_mod

    json_output = export_json(data, "recommendation-list")
    parsed = json_mod.loads(json_output)

    for record in parsed["data"]:
        for pii_field in PII_FIELDS:
            assert pii_field not in record, f"PII field '{pii_field}' in JSON export"


@given(
    nested=st.fixed_dictionaries({
        "level1": st.fixed_dictionaries({
            "sanitizedText": _safe_text,
            "normalField": _safe_text,
            "level2": st.fixed_dictionaries({
                "freeTextInput": _safe_text,
                "anotherField": _safe_text,
            }),
        }),
    }),
)
@settings(max_examples=100)
def test_strip_pii_works_recursively(nested):
    """stripPII recursively removes PII fields from nested objects."""
    result = strip_pii(nested)

    assert "sanitizedText" not in result["level1"]
    assert "normalField" in result["level1"]
    assert "freeTextInput" not in result["level1"]["level2"]
    assert "anotherField" in result["level1"]["level2"]
