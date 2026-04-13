"""Property 9: Intent Coverage Metric Computation

For any pair of real-input and accuracy normalized record sets, the comparison
engine should produce one IntentCoverageMetric per unique intent across both
sets, where: real-input count equals the number of real records with that intent,
golden-set count equals the number of golden records with that intent, share
percentages sum to 100% across all intents within each dataset, and
representation delta equals real share minus golden share.

**Validates: Requirements 5.1, 5.2**
"""

from __future__ import annotations

# Feature: python-analysis-backend, Property 9: Intent Coverage Metric Computation

import math

from hypothesis import given, settings, assume
from hypothesis import strategies as st

from engine.comparison import ComparisonConfig, compare_intent_coverage

# ─── Strategies ──────────────────────────────────────────────────────────────

_intent_names = st.sampled_from([
    "product-search", "price-filter", "color-filter", "size-filter",
    "brand-filter", "sort-by-rating", "return-policy", "gift-wrap",
])


def _normalized_record(intent_st=_intent_names):
    return st.fixed_dictionaries({
        "normalizedIntent": intent_st,
        "normalizedStatus": st.just("results-found"),
        "normalizedOptions": st.just([]),
        "originalValues": st.just({}),
        "originalSourceId": st.text(min_size=1, max_size=10),
    })


_config = ComparisonConfig(
    run_id="test-run",
    materiality_threshold=0.05,
    min_sample_size=100,
    confidence_level=0.95,
    protected_intent_ids=set(),
)


# ─── Property Tests ─────────────────────────────────────────────────────────


@given(
    real_records=st.lists(_normalized_record(), min_size=1, max_size=30),
    golden_records=st.lists(_normalized_record(), min_size=1, max_size=30),
)
@settings(max_examples=100)
def test_one_metric_per_unique_intent(real_records, golden_records):
    """The comparison produces exactly one metric per unique intent across both sets."""
    metrics = compare_intent_coverage(real_records, golden_records, _config)

    real_intents = {r["normalizedIntent"] for r in real_records}
    golden_intents = {r["normalizedIntent"] for r in golden_records}
    all_intents = real_intents | golden_intents

    metric_intents = {m["intentId"] for m in metrics}
    assert metric_intents == all_intents
    assert len(metrics) == len(all_intents)


@given(
    real_records=st.lists(_normalized_record(), min_size=1, max_size=30),
    golden_records=st.lists(_normalized_record(), min_size=1, max_size=30),
)
@settings(max_examples=100)
def test_real_input_counts_correct(real_records, golden_records):
    """Real-input count for each intent equals the number of real records with that intent."""
    metrics = compare_intent_coverage(real_records, golden_records, _config)

    # Count real records per intent
    expected_counts: dict[str, int] = {}
    for r in real_records:
        intent = r["normalizedIntent"]
        expected_counts[intent] = expected_counts.get(intent, 0) + 1

    for m in metrics:
        expected = expected_counts.get(m["intentId"], 0)
        assert m["realInputCount"] == expected


@given(
    real_records=st.lists(_normalized_record(), min_size=1, max_size=30),
    golden_records=st.lists(_normalized_record(), min_size=1, max_size=30),
)
@settings(max_examples=100)
def test_golden_set_counts_correct(real_records, golden_records):
    """Golden-set count for each intent equals the number of golden records with that intent."""
    metrics = compare_intent_coverage(real_records, golden_records, _config)

    expected_counts: dict[str, int] = {}
    for r in golden_records:
        intent = r["normalizedIntent"]
        expected_counts[intent] = expected_counts.get(intent, 0) + 1

    for m in metrics:
        expected = expected_counts.get(m["intentId"], 0)
        assert m["goldenSetCaseCount"] == expected


@given(
    real_records=st.lists(_normalized_record(), min_size=1, max_size=30),
    golden_records=st.lists(_normalized_record(), min_size=1, max_size=30),
)
@settings(max_examples=100)
def test_share_percentages_sum_to_100(real_records, golden_records):
    """Share percentages sum to approximately 100% across all intents within each dataset."""
    metrics = compare_intent_coverage(real_records, golden_records, _config)

    real_share_sum = sum(m["realInputSharePercent"] for m in metrics)
    golden_share_sum = sum(m["goldenSetSharePercent"] for m in metrics)

    # Real shares should sum to 100% (or 0% if no real records contribute)
    assert abs(real_share_sum - 100.0) < 0.01

    # Golden shares should sum to 100%
    assert abs(golden_share_sum - 100.0) < 0.01


@given(
    real_records=st.lists(_normalized_record(), min_size=1, max_size=30),
    golden_records=st.lists(_normalized_record(), min_size=1, max_size=30),
)
@settings(max_examples=100)
def test_representation_delta_equals_real_minus_golden(real_records, golden_records):
    """Representation delta equals real share minus golden share (in percentage points)."""
    metrics = compare_intent_coverage(real_records, golden_records, _config)

    for m in metrics:
        expected_delta = m["realInputSharePercent"] - m["goldenSetSharePercent"]
        assert abs(m["representationDelta"] - expected_delta) < 0.001
