"""Property 15: Recommendation Business Rules

For any set of coverage metrics, stability metrics, and paraphrase metrics,
the recommendation engine should produce recommendations matching the business
rules: real-only + action-ready -> add-new-intent; real-only + monitor ->
watchlist add-new-intent; underrepresented -> add-examples-for-intent;
unsupported above materiality -> add-unsupported-coverage; policy/PII/non-English
without golden coverage -> add-policy-pii-coverage; candidate-obsolete ->
reduce-retire-obsolete; matched -> no-update.

**Validates: Requirements 8.1, 8.2**
"""

from __future__ import annotations

# Feature: python-analysis-backend, Property 15: Recommendation Business Rules

from hypothesis import given, settings, assume
from hypothesis import strategies as st

from engine.recommendation_engine import (
    RecommendationEngineConfig,
    generate_recommendations,
)

# ─── Strategies ──────────────────────────────────────────────────────────────

_intent_names = st.sampled_from([
    "product-search", "price-filter", "color-filter", "size-filter",
    "brand-filter", "sort-by-rating", "return-policy", "gift-wrap",
])

_actionability = st.sampled_from([
    "action-ready", "monitor", "insufficient-evidence", "protected-override",
])

_classification = st.sampled_from([
    "matched", "real-only", "underrepresented", "overrepresented",
    "candidate-obsolete", "protected-retained", "golden-only",
])


def _coverage_metric(
    classification_st=_classification,
    actionability_st=_actionability,
):
    return st.fixed_dictionaries({
        "intentId": _intent_names,
        "intentLabel": _intent_names,
        "intentFamily": st.just(""),
        "classification": classification_st,
        "realInputCount": st.integers(min_value=0, max_value=500),
        "realInputSharePercent": st.floats(min_value=0, max_value=100, allow_nan=False),
        "goldenSetCaseCount": st.integers(min_value=0, max_value=500),
        "goldenSetSharePercent": st.floats(min_value=0, max_value=100, allow_nan=False),
        "representationDelta": st.floats(min_value=-50, max_value=50, allow_nan=False),
        "isProtected": st.just(False),
        "protectedClasses": st.just([]),
        "actionability": actionability_st,
    })


_config = RecommendationEngineConfig(
    run_id="test-run",
    materiality_threshold=0.05,
    protected_case_rules=[],
    observation_window=30,
)


# ─── Property Tests ─────────────────────────────────────────────────────────


@given(
    intent_id=_intent_names,
    share=st.floats(min_value=0.1, max_value=100, allow_nan=False),
)
@settings(max_examples=100)
def test_real_only_action_ready_produces_add_new_intent(intent_id, share):
    """real-only + action-ready -> add-new-intent."""
    metric = {
        "intentId": intent_id,
        "intentLabel": intent_id,
        "intentFamily": "",
        "classification": "real-only",
        "realInputCount": 10,
        "realInputSharePercent": share,
        "goldenSetCaseCount": 0,
        "goldenSetSharePercent": 0,
        "representationDelta": share,
        "isProtected": False,
        "protectedClasses": [],
        "actionability": "action-ready",
    }
    stability = [{
        "intentId": intent_id,
        "actionability": "action-ready",
    }]

    recs = generate_recommendations([metric], stability, [], _config)
    add_new = [r for r in recs if r["type"] == "add-new-intent" and r["impactedIntentId"] == intent_id]
    assert len(add_new) >= 1
    assert add_new[0]["actionability"] == "action-ready"


@given(
    intent_id=_intent_names,
    share=st.floats(min_value=0.1, max_value=100, allow_nan=False),
)
@settings(max_examples=100)
def test_real_only_monitor_produces_watchlist(intent_id, share):
    """real-only + monitor -> watchlist add-new-intent with monitor actionability."""
    metric = {
        "intentId": intent_id,
        "intentLabel": intent_id,
        "intentFamily": "",
        "classification": "real-only",
        "realInputCount": 10,
        "realInputSharePercent": share,
        "goldenSetCaseCount": 0,
        "goldenSetSharePercent": 0,
        "representationDelta": share,
        "isProtected": False,
        "protectedClasses": [],
        "actionability": "monitor",
    }
    stability = [{
        "intentId": intent_id,
        "actionability": "monitor",
    }]

    recs = generate_recommendations([metric], stability, [], _config)
    add_new = [r for r in recs if r["type"] == "add-new-intent" and r["impactedIntentId"] == intent_id]
    assert len(add_new) >= 1
    assert add_new[0]["actionability"] == "monitor"


@given(
    intent_id=_intent_names,
    real_share=st.floats(min_value=1, max_value=100, allow_nan=False),
    golden_share=st.floats(min_value=0, max_value=50, allow_nan=False),
)
@settings(max_examples=100)
def test_underrepresented_produces_add_examples(intent_id, real_share, golden_share):
    """underrepresented -> add-examples-for-intent."""
    metric = {
        "intentId": intent_id,
        "intentLabel": intent_id,
        "intentFamily": "",
        "classification": "underrepresented",
        "realInputCount": 50,
        "realInputSharePercent": real_share,
        "goldenSetCaseCount": 10,
        "goldenSetSharePercent": golden_share,
        "representationDelta": real_share - golden_share,
        "isProtected": False,
        "protectedClasses": [],
        "actionability": "action-ready",
    }

    recs = generate_recommendations([metric], [], [], _config)
    add_examples = [r for r in recs if r["type"] == "add-examples-for-intent"]
    assert len(add_examples) >= 1


@given(intent_id=_intent_names)
@settings(max_examples=100)
def test_candidate_obsolete_produces_reduce_retire(intent_id):
    """candidate-obsolete -> reduce-retire-obsolete."""
    metric = {
        "intentId": intent_id,
        "intentLabel": intent_id,
        "intentFamily": "",
        "classification": "candidate-obsolete",
        "realInputCount": 0,
        "realInputSharePercent": 0,
        "goldenSetCaseCount": 5,
        "goldenSetSharePercent": 10,
        "representationDelta": -10,
        "isProtected": False,
        "protectedClasses": [],
        "actionability": "insufficient-evidence",
    }

    recs = generate_recommendations([metric], [], [], _config)
    retire = [r for r in recs if r["type"] == "reduce-retire-obsolete"]
    assert len(retire) >= 1


@given(
    intent_id=_intent_names,
    share=st.floats(min_value=0, max_value=100, allow_nan=False),
)
@settings(max_examples=100)
def test_matched_produces_no_update(intent_id, share):
    """matched -> no-update."""
    metric = {
        "intentId": intent_id,
        "intentLabel": intent_id,
        "intentFamily": "",
        "classification": "matched",
        "realInputCount": 50,
        "realInputSharePercent": share,
        "goldenSetCaseCount": 50,
        "goldenSetSharePercent": share,
        "representationDelta": 0,
        "isProtected": False,
        "protectedClasses": [],
        "actionability": "action-ready",
    }

    recs = generate_recommendations([metric], [], [], _config)
    no_update = [r for r in recs if r["type"] == "no-update"]
    assert len(no_update) >= 1


@given(
    intent_id=_intent_names,
    share=st.floats(min_value=0.05, max_value=100, allow_nan=False),
)
@settings(max_examples=100)
def test_unsupported_above_materiality_produces_coverage(intent_id, share):
    """unsupported intent above materiality -> add-unsupported-coverage."""
    metric = {
        "intentId": intent_id,
        "intentLabel": intent_id,
        "intentFamily": "",
        "classification": "real-only",
        "realInputCount": 10,
        "realInputSharePercent": share,
        "goldenSetCaseCount": 0,
        "goldenSetSharePercent": 0,
        "representationDelta": share,
        "isProtected": True,
        "protectedClasses": ["unsupported-intent"],
        "actionability": "protected-override",
    }

    recs = generate_recommendations([metric], [], [], _config)
    unsupported = [r for r in recs if r["type"] == "add-unsupported-coverage"]
    assert len(unsupported) >= 1


@given(intent_id=_intent_names)
@settings(max_examples=100)
def test_policy_pii_without_golden_produces_coverage(intent_id):
    """policy/PII/non-English protected intent without golden coverage -> add-policy-pii-coverage."""
    metric = {
        "intentId": intent_id,
        "intentLabel": intent_id,
        "intentFamily": "",
        "classification": "real-only",
        "realInputCount": 5,
        "realInputSharePercent": 2.0,
        "goldenSetCaseCount": 0,
        "goldenSetSharePercent": 0,
        "representationDelta": 2.0,
        "isProtected": True,
        "protectedClasses": ["policy-blocked"],
        "actionability": "protected-override",
    }

    recs = generate_recommendations([metric], [], [], _config)
    policy = [r for r in recs if r["type"] == "add-policy-pii-coverage"]
    assert len(policy) >= 1
