"""Property 5: Record Validation Rejects Invalid Records

For any dataset type and for any record missing a required field for that type,
the validator should report at least one error mentioning the missing field.

**Validates: Requirements 3.6, 12.1, 12.2, 12.3, 12.4, 12.5, 12.6**
"""

from __future__ import annotations

from hypothesis import given, settings, assume
from hypothesis import strategies as st

from engine.schemas import (
    validate_import_record,
    validate_real_input_record,
    validate_accuracy_golden_set_record,
    validate_consistency_golden_set_record,
    validate_status_mapping_record,
)


# ─── Required fields per dataset type ───────────────────────────────────────

REAL_INPUT_REQUIRED = ["recordId", "observedAt", "sanitizedText"]

ACCURACY_REQUIRED = [
    "testCaseId", "businessRequirement", "scenario", "freeTextInput",
    "expectedOptions", "expectedStatus", "canonicalIntent", "goldenSetVersion",
]

CONSISTENCY_REQUIRED = [
    "sourceTestCaseId", "variantId", "businessRequirement", "scenario",
    "freeTextInput", "expectedOptions", "expectedStatus", "canonicalIntent",
    "goldenSetVersion",
]

STATUS_MAPPING_REQUIRED = ["statusCode", "businessMeaning", "statusClass"]


# ─── Hypothesis Strategies ───────────────────────────────────────────────────

_nonempty_str = st.text(
    alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyz0123456789"),
    min_size=1,
    max_size=20,
)


def _valid_real_input():
    return st.fixed_dictionaries({
        "recordId": _nonempty_str,
        "observedAt": _nonempty_str,
        "sanitizedText": _nonempty_str,
    })


def _valid_accuracy():
    return st.fixed_dictionaries({
        "testCaseId": _nonempty_str,
        "businessRequirement": _nonempty_str,
        "scenario": _nonempty_str,
        "freeTextInput": _nonempty_str,
        "expectedOptions": st.just(["option1"]),
        "expectedStatus": _nonempty_str,
        "canonicalIntent": _nonempty_str,
        "goldenSetVersion": _nonempty_str,
    })


def _valid_consistency():
    return st.fixed_dictionaries({
        "sourceTestCaseId": _nonempty_str,
        "variantId": _nonempty_str,
        "businessRequirement": _nonempty_str,
        "scenario": _nonempty_str,
        "freeTextInput": _nonempty_str,
        "expectedOptions": st.just(["option1"]),
        "expectedStatus": _nonempty_str,
        "canonicalIntent": _nonempty_str,
        "goldenSetVersion": _nonempty_str,
    })


def _valid_status_mapping():
    return st.fixed_dictionaries({
        "statusCode": _nonempty_str,
        "businessMeaning": _nonempty_str,
        "statusClass": _nonempty_str,
    })


# ─── Property Tests ─────────────────────────────────────────────────────────
# Feature: python-analysis-backend, Property 5: Record Validation Rejects Invalid Records


@given(
    record=_valid_real_input(),
    field_to_remove=st.sampled_from(REAL_INPUT_REQUIRED),
)
@settings(max_examples=100)
def test_real_input_missing_required_field(record, field_to_remove):
    """Removing any required field from a real-input record causes validation failure."""
    record = dict(record)  # copy
    del record[field_to_remove]

    result = validate_import_record(record, "real-input")

    assert not result.valid
    assert len(result.errors) > 0
    # At least one error should mention the missing field
    assert any(field_to_remove in err for err in result.errors)


@given(
    record=_valid_accuracy(),
    field_to_remove=st.sampled_from(ACCURACY_REQUIRED),
)
@settings(max_examples=100)
def test_accuracy_missing_required_field(record, field_to_remove):
    """Removing any required field from an accuracy record causes validation failure."""
    record = dict(record)
    del record[field_to_remove]

    result = validate_import_record(record, "accuracy-golden-set")

    assert not result.valid
    assert len(result.errors) > 0
    assert any(field_to_remove in err for err in result.errors)


@given(
    record=_valid_consistency(),
    field_to_remove=st.sampled_from(CONSISTENCY_REQUIRED),
)
@settings(max_examples=100)
def test_consistency_missing_required_field(record, field_to_remove):
    """Removing any required field from a consistency record causes validation failure."""
    record = dict(record)
    del record[field_to_remove]

    result = validate_import_record(record, "consistency-golden-set")

    assert not result.valid
    assert len(result.errors) > 0
    assert any(field_to_remove in err for err in result.errors)


@given(
    record=_valid_status_mapping(),
    field_to_remove=st.sampled_from(STATUS_MAPPING_REQUIRED),
)
@settings(max_examples=100)
def test_status_mapping_missing_required_field(record, field_to_remove):
    """Removing any required field from a status-mapping record causes validation failure."""
    record = dict(record)
    del record[field_to_remove]

    result = validate_import_record(record, "status-mapping")

    assert not result.valid
    assert len(result.errors) > 0
    assert any(field_to_remove in err for err in result.errors)


@given(record=_valid_real_input())
@settings(max_examples=100)
def test_valid_real_input_passes(record):
    """A complete valid real-input record passes validation."""
    result = validate_import_record(record, "real-input")
    assert result.valid
    assert len(result.errors) == 0


@given(record=_valid_accuracy())
@settings(max_examples=100)
def test_valid_accuracy_passes(record):
    """A complete valid accuracy record passes validation."""
    result = validate_import_record(record, "accuracy-golden-set")
    assert result.valid
    assert len(result.errors) == 0


@given(record=_valid_consistency())
@settings(max_examples=100)
def test_valid_consistency_passes(record):
    """A complete valid consistency record passes validation."""
    result = validate_import_record(record, "consistency-golden-set")
    assert result.valid
    assert len(result.errors) == 0


@given(record=_valid_status_mapping())
@settings(max_examples=100)
def test_valid_status_mapping_passes(record):
    """A complete valid status-mapping record passes validation."""
    result = validate_import_record(record, "status-mapping")
    assert result.valid
    assert len(result.errors) == 0


def test_non_object_payload_rejected():
    """Non-object payloads are rejected for all dataset types."""
    for dt in ["real-input", "accuracy-golden-set", "consistency-golden-set", "status-mapping"]:
        result = validate_import_record("not an object", dt)
        assert not result.valid
        assert any("object" in err.lower() for err in result.errors)


def test_reference_catalog_accepts_any_object():
    """Reference catalogs accept any object."""
    result = validate_import_record({"anything": "goes"}, "reference-catalog")
    assert result.valid


def test_unknown_dataset_type_rejected():
    """Unknown dataset types are rejected."""
    result = validate_import_record({}, "unknown-type")
    assert not result.valid
    assert any("Unknown dataset type" in err for err in result.errors)
