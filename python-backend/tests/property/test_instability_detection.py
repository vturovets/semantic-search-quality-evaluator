"""Property 14: Instability Detection

For any set of normalized real-input records where the same canonical intent
has N > 1 distinct normalized statuses, the instability detector should report
hasInstabilitySignal = true and outcomeVariability should contain exactly those
N distinct statuses.

**Validates: Requirements 7.4, 7.5**
"""

from __future__ import annotations

# Feature: python-analysis-backend, Property 14: Instability Detection

from hypothesis import given, settings, assume
from hypothesis import strategies as st

from engine.consistency_metrics import detect_instability

# ─── Strategies ──────────────────────────────────────────────────────────────

_intent = st.sampled_from(["product-search", "price-filter", "color-filter", "size-filter"])
_status = st.sampled_from([
    "results-found", "no-results", "option-applied", "info-displayed",
    "blocked", "unsupported", "pii-redacted",
])


def _record(intent_st=_intent, status_st=_status):
    return st.fixed_dictionaries({
        "normalizedIntent": intent_st,
        "normalizedStatus": status_st,
        "normalizedOptions": st.just([]),
        "originalSourceId": st.text(min_size=1, max_size=10),
        "originalValues": st.just({}),
    })


# ─── Property Tests ─────────────────────────────────────────────────────────


@given(
    target_intent=_intent,
    statuses=st.lists(_status, min_size=2, max_size=7, unique=True),
)
@settings(max_examples=100)
def test_multiple_statuses_signal_instability(target_intent, statuses):
    """When an intent has N > 1 distinct statuses, hasInstability is true
    and statuses contains exactly those N values."""
    # Build records with the target intent and different statuses
    records = [
        {
            "normalizedIntent": target_intent,
            "normalizedStatus": s,
            "normalizedOptions": [],
            "originalSourceId": f"rec-{i}",
            "originalValues": {},
        }
        for i, s in enumerate(statuses)
    ]

    result = detect_instability(target_intent, records)

    assert result["hasInstability"] is True
    assert set(result["statuses"]) == set(statuses)
    assert len(result["statuses"]) == len(statuses)


@given(
    target_intent=_intent,
    single_status=_status,
    count=st.integers(min_value=1, max_value=10),
)
@settings(max_examples=100)
def test_single_status_no_instability(target_intent, single_status, count):
    """When an intent has only one distinct status, hasInstability is false."""
    records = [
        {
            "normalizedIntent": target_intent,
            "normalizedStatus": single_status,
            "normalizedOptions": [],
            "originalSourceId": f"rec-{i}",
            "originalValues": {},
        }
        for i in range(count)
    ]

    result = detect_instability(target_intent, records)

    assert result["hasInstability"] is False
    assert result["statuses"] == [single_status]


@given(
    target_intent=st.just("product-search"),
    other_intent=st.just("price-filter"),
    statuses=st.lists(_status, min_size=2, max_size=5, unique=True),
)
@settings(max_examples=100)
def test_only_matching_intent_records_considered(target_intent, other_intent, statuses):
    """Only records matching the target intent are considered for instability."""
    assume(target_intent != other_intent)

    # Records for target intent with single status
    target_records = [
        {
            "normalizedIntent": target_intent,
            "normalizedStatus": "results-found",
            "normalizedOptions": [],
            "originalSourceId": f"target-{i}",
            "originalValues": {},
        }
        for i in range(3)
    ]

    # Records for other intent with multiple statuses
    other_records = [
        {
            "normalizedIntent": other_intent,
            "normalizedStatus": s,
            "normalizedOptions": [],
            "originalSourceId": f"other-{i}",
            "originalValues": {},
        }
        for i, s in enumerate(statuses)
    ]

    all_records = target_records + other_records
    result = detect_instability(target_intent, all_records)

    # Target intent has only one status, so no instability
    assert result["hasInstability"] is False
    assert result["statuses"] == ["results-found"]


@given(target_intent=_intent)
@settings(max_examples=100)
def test_no_records_no_instability(target_intent):
    """When there are no records for the intent, no instability is detected."""
    result = detect_instability(target_intent, [])

    assert result["hasInstability"] is False
    assert result["statuses"] == []
