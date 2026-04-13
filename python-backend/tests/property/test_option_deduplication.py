"""Property 8: Option Deduplication Preserves Order

For any list of option strings that may contain duplicates after normalization,
the normalized options list should contain no duplicates, and the relative order
of first occurrences should be preserved.

**Validates: Requirements 4.4**
"""

from __future__ import annotations

# Feature: python-analysis-backend, Property 8: Option Deduplication Preserves Order

from hypothesis import given, settings
from hypothesis import strategies as st

from engine.normalization import DEFAULT_RULE_TABLE, normalize_options

# ─── Strategies ──────────────────────────────────────────────────────────────

_option_key = st.sampled_from(sorted(DEFAULT_RULE_TABLE.option_normalization.keys()))
_arbitrary_option = st.text(
    alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyz0123456789:-_"),
    min_size=1,
    max_size=30,
)
_mixed_option = st.one_of(_option_key, _arbitrary_option)


# ─── Property Tests ─────────────────────────────────────────────────────────


@given(options=st.lists(_mixed_option, min_size=0, max_size=10))
@settings(max_examples=100)
def test_no_duplicates_in_normalized_options(options):
    """Normalized options list never contains duplicates."""
    result = normalize_options(options, DEFAULT_RULE_TABLE)
    assert len(result.values) == len(set(result.values))


@given(options=st.lists(_mixed_option, min_size=0, max_size=10))
@settings(max_examples=100)
def test_first_occurrence_order_preserved(options):
    """The relative order of first occurrences is preserved after deduplication."""
    result = normalize_options(options, DEFAULT_RULE_TABLE)

    # Build expected order: normalize each option, keep first occurrence
    seen: set[str] = set()
    expected_order: list[str] = []
    for opt in options:
        key = opt.strip().lower()
        normalized = DEFAULT_RULE_TABLE.option_normalization.get(key, key)
        if normalized not in seen:
            seen.add(normalized)
            expected_order.append(normalized)

    assert result.values == expected_order


@given(
    base_options=st.lists(_option_key, min_size=1, max_size=5),
)
@settings(max_examples=100)
def test_duplicates_from_synonyms_are_collapsed(base_options):
    """When multiple input options normalize to the same canonical value,
    only the first occurrence is kept."""
    # Create a list with duplicates by repeating
    options_with_dupes = base_options + base_options
    result = normalize_options(options_with_dupes, DEFAULT_RULE_TABLE)

    # No duplicates
    assert len(result.values) == len(set(result.values))

    # All values should be canonical forms
    for v in result.values:
        assert v in DEFAULT_RULE_TABLE.option_normalization.values() or v == v.strip().lower()


@given(options=st.lists(_mixed_option, min_size=0, max_size=10))
@settings(max_examples=100)
def test_all_original_options_represented(options):
    """Every unique normalized value from the input appears in the output."""
    result = normalize_options(options, DEFAULT_RULE_TABLE)

    # Build set of expected normalized values
    expected: set[str] = set()
    for opt in options:
        key = opt.strip().lower()
        normalized = DEFAULT_RULE_TABLE.option_normalization.get(key, key)
        expected.add(normalized)

    assert set(result.values) == expected
