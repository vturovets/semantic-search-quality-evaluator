"""Property 13: Paraphrase Group Classification and Uncovered Variants

For any set of real-input and consistency normalized records, the wording
coverage comparison should: classify protected intents as protected-retained;
classify groups with zero real variants as missing; classify groups with
uncovered variants as narrow; classify fully covered groups as
adequately-represented. The uncovered variants set should equal the set
difference of real wordings minus golden wordings.

**Validates: Requirements 7.1, 7.2, 7.3**
"""

from __future__ import annotations

# Feature: python-analysis-backend, Property 13: Paraphrase Group Classification and Uncovered Variants

from hypothesis import given, settings, assume
from hypothesis import strategies as st

from engine.comparison import (
    ComparisonConfig,
    classify_paraphrase_group,
    compare_wording_coverage,
)

# ─── Strategies ──────────────────────────────────────────────────────────────

_intent = st.sampled_from(["product-search", "price-filter", "color-filter"])
_text = st.text(
    alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyz "),
    min_size=1,
    max_size=30,
)


def _consistency_record(intent_st=_intent, group_id_st=st.just("group-1")):
    return st.fixed_dictionaries({
        "normalizedIntent": intent_st,
        "normalizedStatus": st.just("results-found"),
        "normalizedOptions": st.just([]),
        "originalSourceId": st.text(min_size=1, max_size=10),
        "originalValues": st.builds(
            lambda g, t: {"sourceTestCaseId": g, "freeTextInput": t},
            g=group_id_st,
            t=_text,
        ),
    })


def _real_record(intent_st=_intent):
    return st.fixed_dictionaries({
        "normalizedIntent": intent_st,
        "normalizedStatus": st.sampled_from(["results-found", "no-results"]),
        "normalizedOptions": st.just([]),
        "originalSourceId": st.text(min_size=1, max_size=10),
        "originalValues": st.builds(
            lambda t: {"sanitizedText": t},
            t=_text,
        ),
    })


# ─── Property Tests ─────────────────────────────────────────────────────────


@given(
    golden_count=st.integers(min_value=1, max_value=10),
    real_variant_count=st.integers(min_value=0, max_value=10),
    uncovered_count=st.integers(min_value=0, max_value=10),
)
@settings(max_examples=100)
def test_protected_always_protected_retained(golden_count, real_variant_count, uncovered_count):
    """Protected intents are always classified as protected-retained."""
    result = classify_paraphrase_group(golden_count, real_variant_count, uncovered_count, True)
    assert result == "protected-retained"


@given(golden_count=st.integers(min_value=1, max_value=10))
@settings(max_examples=100)
def test_zero_real_variants_is_missing(golden_count):
    """Groups with zero real wording variants are classified as missing."""
    result = classify_paraphrase_group(golden_count, 0, 0, False)
    assert result == "missing"


@given(
    golden_count=st.integers(min_value=1, max_value=10),
    real_variant_count=st.integers(min_value=1, max_value=10),
    uncovered_count=st.integers(min_value=1, max_value=10),
)
@settings(max_examples=100)
def test_uncovered_variants_is_narrow(golden_count, real_variant_count, uncovered_count):
    """Groups with uncovered variants (> 0) are classified as narrow."""
    result = classify_paraphrase_group(golden_count, real_variant_count, uncovered_count, False)
    assert result == "narrow"


@given(
    golden_count=st.integers(min_value=1, max_value=10),
    real_variant_count=st.integers(min_value=1, max_value=10),
)
@settings(max_examples=100)
def test_fully_covered_is_adequately_represented(golden_count, real_variant_count):
    """Groups with zero uncovered variants are classified as adequately-represented."""
    result = classify_paraphrase_group(golden_count, real_variant_count, 0, False)
    assert result == "adequately-represented"


@given(
    consistency_records=st.lists(
        _consistency_record(intent_st=st.just("product-search"), group_id_st=st.just("g1")),
        min_size=1,
        max_size=5,
    ),
    real_records=st.lists(
        _real_record(intent_st=st.just("product-search")),
        min_size=1,
        max_size=5,
    ),
)
@settings(max_examples=100)
def test_uncovered_variants_are_set_difference(consistency_records, real_records):
    """Uncovered variants equal the set difference of real wordings minus golden wordings."""
    config = ComparisonConfig(
        run_id="test",
        materiality_threshold=0.05,
        min_sample_size=100,
        confidence_level=0.95,
        protected_intent_ids=set(),
    )

    metrics = compare_wording_coverage(real_records, consistency_records, config)

    for m in metrics:
        # Collect golden wordings for this group
        golden_wordings: set[str] = set()
        for r in consistency_records:
            ov = r.get("originalValues", {})
            if ov.get("sourceTestCaseId") == m["paraphraseGroupId"]:
                text = ov.get("freeTextInput") or ov.get("sanitizedText") or ""
                if text:
                    golden_wordings.add(text)

        # Collect real wordings for this intent
        real_wordings: set[str] = set()
        for r in real_records:
            if r.get("normalizedIntent") == m["intentId"]:
                ov = r.get("originalValues", {})
                text = ov.get("sanitizedText") or ov.get("freeTextInput") or ""
                if text:
                    real_wordings.add(text)

        expected_uncovered = real_wordings - golden_wordings
        assert set(m["uncoveredVariants"]) == expected_uncovered
