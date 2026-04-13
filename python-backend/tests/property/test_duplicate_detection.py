"""Property 4: Duplicate Detection

For any dataset containing records with duplicate identifier fields, the parser
should report exactly one warning per duplicate pair, and the warning count should
equal the number of duplicate occurrences minus one per unique ID.

**Validates: Requirements 3.7**
"""

from __future__ import annotations

from collections import Counter

from hypothesis import given, settings
from hypothesis import strategies as st

from engine.parser import check_duplicate_ids


# ─── Hypothesis Strategies ───────────────────────────────────────────────────

_id_value = st.text(
    alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyz0123456789"),
    min_size=1,
    max_size=10,
)


@st.composite
def _records_with_duplicates(draw):
    """Generate records with known duplicate structure for real-input dataset type.

    Returns (records, expected_duplicate_warning_count).
    """
    # Generate a pool of unique IDs
    n_unique = draw(st.integers(min_value=1, max_value=5))
    unique_ids = draw(
        st.lists(_id_value, min_size=n_unique, max_size=n_unique, unique=True)
    )

    # For each unique ID, decide how many times it appears (1 to 3)
    counts = draw(
        st.lists(
            st.integers(min_value=1, max_value=3),
            min_size=n_unique,
            max_size=n_unique,
        )
    )

    records = []
    for uid, count in zip(unique_ids, counts):
        for _ in range(count):
            records.append({"recordId": uid})

    # Expected warnings: for each ID appearing N times, N-1 warnings
    expected_warnings = sum(c - 1 for c in counts)

    return records, expected_warnings


@st.composite
def _composite_key_records_with_duplicates(draw):
    """Generate records with composite keys for consistency-golden-set.

    Returns (records, expected_duplicate_warning_count).
    """
    n_unique = draw(st.integers(min_value=1, max_value=5))
    unique_keys = draw(
        st.lists(
            st.tuples(_id_value, _id_value),
            min_size=n_unique,
            max_size=n_unique,
            unique=True,
        )
    )

    counts = draw(
        st.lists(
            st.integers(min_value=1, max_value=3),
            min_size=n_unique,
            max_size=n_unique,
        )
    )

    records = []
    for (src_id, var_id), count in zip(unique_keys, counts):
        for _ in range(count):
            records.append({"sourceTestCaseId": src_id, "variantId": var_id})

    expected_warnings = sum(c - 1 for c in counts)

    return records, expected_warnings


# ─── Property Tests ─────────────────────────────────────────────────────────
# Feature: python-analysis-backend, Property 4: Duplicate Detection


@given(data=_records_with_duplicates())
@settings(max_examples=100)
def test_single_field_duplicate_count(data):
    """For single-field IDs, warning count equals total duplicates minus one per unique ID."""
    records, expected_warnings = data
    issues: list[dict] = []

    check_duplicate_ids(records, "real-input", issues)

    duplicate_warnings = [i for i in issues if i["severity"] == "warning" and "Duplicate" in i["message"]]
    assert len(duplicate_warnings) == expected_warnings


@given(data=_composite_key_records_with_duplicates())
@settings(max_examples=100)
def test_composite_key_duplicate_count(data):
    """For composite keys, warning count equals total duplicates minus one per unique key."""
    records, expected_warnings = data
    issues: list[dict] = []

    check_duplicate_ids(records, "consistency-golden-set", issues)

    duplicate_warnings = [i for i in issues if i["severity"] == "warning" and "Duplicate" in i["message"]]
    assert len(duplicate_warnings) == expected_warnings


@given(
    records=st.lists(
        st.fixed_dictionaries({"recordId": _id_value}),
        min_size=1,
        max_size=10,
        unique_by=lambda r: r["recordId"],
    )
)
@settings(max_examples=100)
def test_no_duplicates_no_warnings(records):
    """When all IDs are unique, no duplicate warnings are produced."""
    issues: list[dict] = []

    check_duplicate_ids(records, "real-input", issues)

    duplicate_warnings = [i for i in issues if i["severity"] == "warning" and "Duplicate" in i["message"]]
    assert len(duplicate_warnings) == 0


def test_reference_catalog_no_duplicate_check():
    """Reference catalogs have no ID field, so no duplicate checking occurs."""
    records = [{"key": "a"}, {"key": "a"}]
    issues: list[dict] = []

    check_duplicate_ids(records, "reference-catalog", issues)

    assert len(issues) == 0
