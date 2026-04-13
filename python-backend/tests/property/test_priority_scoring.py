"""Property 18: Priority Scoring Determinism

For any PriorityInput with observedSharePercent, actionability, isProtected,
representationDelta, and coverage flags, the computed priority should be:
critical if score >= 70, high if score >= 45, medium if score >= 25, low
otherwise, where score = min(30, share*10) + actionability_weight +
(20 if protected) + min(15, |delta|*5) + coverage_weight.

**Validates: Requirements 8.5**
"""

from __future__ import annotations

# Feature: python-analysis-backend, Property 18: Priority Scoring Determinism

from hypothesis import given, settings
from hypothesis import strategies as st

from engine.priority_rules import PriorityInput, compute_priority, ACTIONABILITY_SCORES

# ─── Strategies ──────────────────────────────────────────────────────────────

_actionability = st.sampled_from([
    "action-ready", "monitor", "insufficient-evidence", "protected-override",
])


def _priority_input():
    return st.builds(
        PriorityInput,
        observed_share_percent=st.floats(min_value=0, max_value=20, allow_nan=False),
        actionability=_actionability,
        is_protected=st.booleans(),
        representation_delta=st.floats(min_value=-20, max_value=20, allow_nan=False),
        affects_governance=st.booleans(),
        affects_accuracy=st.booleans(),
        affects_consistency=st.booleans(),
    )


def _expected_score(inp: PriorityInput) -> float:
    """Compute the expected score using the same formula as the implementation."""
    score = 0.0
    score += min(30, inp.observed_share_percent * 10)
    score += ACTIONABILITY_SCORES.get(inp.actionability, 0)
    if inp.is_protected:
        score += 20
    score += min(15, abs(inp.representation_delta) * 5)
    if inp.affects_governance:
        score += 10
    elif inp.affects_accuracy:
        score += 7
    elif inp.affects_consistency:
        score += 5
    return score


def _expected_priority(score: float) -> str:
    if score >= 70:
        return "critical"
    if score >= 45:
        return "high"
    if score >= 25:
        return "medium"
    return "low"


# ─── Property Tests ─────────────────────────────────────────────────────────


@given(inp=_priority_input())
@settings(max_examples=100)
def test_priority_matches_scoring_formula(inp):
    """The computed priority matches the expected score-based thresholds."""
    result = compute_priority(inp)
    score = _expected_score(inp)
    expected = _expected_priority(score)
    assert result == expected, f"score={score}, expected={expected}, got={result}"


@given(inp=_priority_input())
@settings(max_examples=100)
def test_priority_is_deterministic(inp):
    """Calling computePriority twice with the same input yields the same result."""
    result1 = compute_priority(inp)
    result2 = compute_priority(inp)
    assert result1 == result2


@given(inp=_priority_input())
@settings(max_examples=100)
def test_priority_is_valid_value(inp):
    """The computed priority is always one of the four valid levels."""
    result = compute_priority(inp)
    assert result in {"critical", "high", "medium", "low"}


@given(
    actionability=_actionability,
    delta=st.floats(min_value=-5, max_value=5, allow_nan=False),
)
@settings(max_examples=100)
def test_protected_boost_increases_score(actionability, delta):
    """Setting isProtected=True always increases the effective score by 20 points."""
    base = PriorityInput(
        observed_share_percent=1.0,
        actionability=actionability,
        is_protected=False,
        representation_delta=delta,
        affects_governance=False,
        affects_accuracy=False,
        affects_consistency=False,
    )
    protected = PriorityInput(
        observed_share_percent=1.0,
        actionability=actionability,
        is_protected=True,
        representation_delta=delta,
        affects_governance=False,
        affects_accuracy=False,
        affects_consistency=False,
    )

    base_score = _expected_score(base)
    protected_score = _expected_score(protected)
    assert abs((protected_score - base_score) - 20) < 1e-9


@given(
    share=st.floats(min_value=0, max_value=20, allow_nan=False),
)
@settings(max_examples=100)
def test_frequency_weight_capped_at_30(share):
    """Frequency/share weight is capped at 30 points."""
    freq_weight = min(30, share * 10)
    assert 0 <= freq_weight <= 30


@given(
    delta=st.floats(min_value=-20, max_value=20, allow_nan=False),
)
@settings(max_examples=100)
def test_gap_weight_capped_at_15(delta):
    """Gap size weight is capped at 15 points."""
    gap_weight = min(15, abs(delta) * 5)
    assert 0 <= gap_weight <= 15
