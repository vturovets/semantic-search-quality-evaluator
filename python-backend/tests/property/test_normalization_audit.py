"""Property 7: Normalization Method and Audit Trail Completeness

For any record normalized by the Normalization Engine, the output should contain
all audit fields (id, createdAt, createdBy, updatedAt, version), original source
ID, original values, normalized values, rule ID, method, and explanation. The
method should be deterministic if and only if all sub-normalizations matched
rule-table entries.

**Validates: Requirements 4.5, 4.6**
"""

from __future__ import annotations

# Feature: python-analysis-backend, Property 7: Normalization Method and Audit Trail Completeness

from hypothesis import given, settings
from hypothesis import strategies as st

from engine.normalization import DEFAULT_RULE_TABLE, normalize_record

# ─── Strategies ──────────────────────────────────────────────────────────────

_nonempty = st.text(
    alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyz0123456789-_"),
    min_size=1,
    max_size=20,
)

_intent_key = st.sampled_from(sorted(DEFAULT_RULE_TABLE.intent_synonyms.keys()))
_status_key = st.sampled_from(sorted(DEFAULT_RULE_TABLE.status_aliases.keys()))
_option_key = st.sampled_from(sorted(DEFAULT_RULE_TABLE.option_normalization.keys()))


def _real_input_record(intent_st=_nonempty, status_st=_nonempty, options_st=st.just([])):
    return st.fixed_dictionaries({
        "recordId": _nonempty,
        "observedAt": _nonempty,
        "sanitizedText": _nonempty,
        "canonicalIntent": intent_st,
        "semanticOutcomeStatus": status_st,
        "appliedOptions": options_st,
    })


# ─── Property Tests ─────────────────────────────────────────────────────────


@given(record=_real_input_record())
@settings(max_examples=100)
def test_audit_fields_always_present(record):
    """Every normalized record has all required audit fields."""
    result = normalize_record(record, "real-input")

    # Audit fields
    assert isinstance(result["id"], str) and len(result["id"]) > 0
    assert isinstance(result["createdAt"], str) and len(result["createdAt"]) > 0
    assert isinstance(result["createdBy"], str) and result["createdBy"] == "normalization-engine"
    assert isinstance(result["updatedAt"], str) and len(result["updatedAt"]) > 0
    assert isinstance(result["version"], int) and result["version"] == 1

    # Source fields
    assert "originalSourceId" in result
    assert "originalSourceType" in result
    assert isinstance(result["originalValues"], dict)

    # Normalized fields
    assert isinstance(result["normalizedIntent"], str)
    assert isinstance(result["normalizedStatus"], str)
    assert isinstance(result["normalizedOptions"], list)

    # Rule and method fields
    assert isinstance(result["normalizationRuleId"], str)
    assert result["normalizationMethod"] in ("deterministic", "heuristic")
    assert isinstance(result["explanation"], str) and len(result["explanation"]) > 0
    assert result["confidence"] is not None


@given(
    record=_real_input_record(
        intent_st=_intent_key,
        status_st=_status_key,
        options_st=st.lists(_option_key, min_size=0, max_size=3),
    )
)
@settings(max_examples=100)
def test_all_rule_table_matches_yield_deterministic(record):
    """When all sub-normalizations match rule-table entries, method is deterministic."""
    result = normalize_record(record, "real-input")
    assert result["normalizationMethod"] == "deterministic"
    assert result["confidence"] == 1.0


@given(
    record=_real_input_record(
        intent_st=st.just("completely-unknown-intent-xyz"),
        status_st=_status_key,
        options_st=st.lists(_option_key, min_size=0, max_size=3),
    )
)
@settings(max_examples=100)
def test_heuristic_intent_yields_heuristic_method(record):
    """When intent doesn't match rule table, overall method is heuristic."""
    result = normalize_record(record, "real-input")
    assert result["normalizationMethod"] == "heuristic"
    assert result["confidence"] == 0.7


@given(
    record=_real_input_record(
        intent_st=_intent_key,
        status_st=st.just("completely-unknown-status-xyz"),
        options_st=st.lists(_option_key, min_size=0, max_size=3),
    )
)
@settings(max_examples=100)
def test_heuristic_status_yields_heuristic_method(record):
    """When status doesn't match rule table, overall method is heuristic."""
    result = normalize_record(record, "real-input")
    assert result["normalizationMethod"] == "heuristic"
    assert result["confidence"] == 0.7


@given(record=_real_input_record())
@settings(max_examples=100)
def test_original_source_type_matches_dataset_type(record):
    """The originalSourceType always matches the dataset type passed in."""
    result = normalize_record(record, "real-input")
    assert result["originalSourceType"] == "real-input"

    # Also test accuracy
    acc_record = {
        "testCaseId": "tc1",
        "businessRequirement": "br",
        "scenario": "sc",
        "freeTextInput": "text",
        "expectedOptions": ["opt1"],
        "expectedStatus": "results-found",
        "canonicalIntent": "product-search",
        "goldenSetVersion": "1.0",
    }
    result2 = normalize_record(acc_record, "accuracy-golden-set")
    assert result2["originalSourceType"] == "accuracy-golden-set"
