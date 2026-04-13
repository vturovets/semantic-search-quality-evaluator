"""Property 6: Normalization Rule Table Lookup

For any key present in the intent synonym map, status alias map, or option
normalization map, normalizing that key should produce the corresponding
canonical value from the map, and the normalization method should be deterministic.

**Validates: Requirements 4.1, 4.2, 4.3**
"""

from __future__ import annotations

# Feature: python-analysis-backend, Property 6: Normalization Rule Table Lookup

from hypothesis import given, settings
from hypothesis import strategies as st

from engine.normalization import (
    DEFAULT_RULE_TABLE,
    normalize_intent,
    normalize_options,
    normalize_status,
)


# ─── Property Tests ─────────────────────────────────────────────────────────


@given(key=st.sampled_from(sorted(DEFAULT_RULE_TABLE.intent_synonyms.keys())))
@settings(max_examples=100)
def test_intent_synonym_lookup_is_deterministic(key: str):
    """Any key in the intent synonym map normalizes to the expected canonical
    value with method 'deterministic'."""
    expected = DEFAULT_RULE_TABLE.intent_synonyms[key]
    result = normalize_intent(key, DEFAULT_RULE_TABLE)

    assert result.value == expected
    assert result.method == "deterministic"


@given(key=st.sampled_from(sorted(DEFAULT_RULE_TABLE.status_aliases.keys())))
@settings(max_examples=100)
def test_status_alias_lookup_is_deterministic(key: str):
    """Any key in the status alias map normalizes to the expected canonical
    value with method 'deterministic'."""
    expected = DEFAULT_RULE_TABLE.status_aliases[key]
    result = normalize_status(key, DEFAULT_RULE_TABLE)

    assert result.value == expected
    assert result.method == "deterministic"


@given(key=st.sampled_from(sorted(DEFAULT_RULE_TABLE.option_normalization.keys())))
@settings(max_examples=100)
def test_option_normalization_lookup_is_deterministic(key: str):
    """Any key in the option normalization map normalizes to the expected
    canonical value with method 'deterministic'."""
    expected = DEFAULT_RULE_TABLE.option_normalization[key]
    result = normalize_options([key], DEFAULT_RULE_TABLE)

    assert result.values == [expected]
    assert result.method == "deterministic"


@given(
    key=st.sampled_from(sorted(DEFAULT_RULE_TABLE.intent_synonyms.keys())),
    case_transform=st.sampled_from(["upper", "title", "identity"]),
)
@settings(max_examples=100)
def test_intent_lookup_is_case_insensitive(key: str, case_transform: str):
    """Intent normalization is case-insensitive: upper/title/identity all
    resolve to the same canonical value."""
    if case_transform == "upper":
        input_key = key.upper()
    elif case_transform == "title":
        input_key = key.title()
    else:
        input_key = key

    expected = DEFAULT_RULE_TABLE.intent_synonyms[key]
    result = normalize_intent(input_key, DEFAULT_RULE_TABLE)

    # The lookup lowercases the input, so it should always match
    assert result.value == expected
    assert result.method == "deterministic"
