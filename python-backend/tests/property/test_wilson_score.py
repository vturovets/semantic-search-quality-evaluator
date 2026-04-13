"""Property 11: Wilson Score Confidence Interval Bounds

For any non-negative integer successes and positive integer total where
successes <= total, the Wilson score confidence interval should satisfy:
0 <= lower <= observedShare <= upper <= 1, and observedShare == successes / total.

**Validates: Requirements 6.1**
"""

from __future__ import annotations

# Feature: python-analysis-backend, Property 11: Wilson Score Confidence Interval Bounds

from hypothesis import given, settings, assume
from hypothesis import strategies as st

from engine.statistical_evaluation import wilson_score_interval

# ─── Strategies ──────────────────────────────────────────────────────────────

_confidence_levels = st.sampled_from([0.80, 0.85, 0.90, 0.95, 0.99])


# ─── Property Tests ─────────────────────────────────────────────────────────


@given(
    successes=st.integers(min_value=0, max_value=10000),
    total=st.integers(min_value=1, max_value=10000),
    confidence_level=_confidence_levels,
)
@settings(max_examples=100)
def test_ci_bounds_are_valid(successes, total, confidence_level):
    """Wilson score CI satisfies 0 <= lower <= observedShare <= upper <= 1."""
    assume(successes <= total)

    ci = wilson_score_interval(successes, total, confidence_level)

    assert ci["lower"] >= 0, f"lower ({ci['lower']}) must be >= 0"
    assert ci["upper"] <= 1, f"upper ({ci['upper']}) must be <= 1"
    assert ci["lower"] <= ci["observedShare"] + 1e-10, (
        f"lower ({ci['lower']}) must be <= observedShare ({ci['observedShare']})"
    )
    assert ci["observedShare"] <= ci["upper"] + 1e-10, (
        f"observedShare ({ci['observedShare']}) must be <= upper ({ci['upper']})"
    )


@given(
    successes=st.integers(min_value=0, max_value=10000),
    total=st.integers(min_value=1, max_value=10000),
    confidence_level=_confidence_levels,
)
@settings(max_examples=100)
def test_observed_share_equals_proportion(successes, total, confidence_level):
    """observedShare equals successes / total."""
    assume(successes <= total)

    ci = wilson_score_interval(successes, total, confidence_level)

    expected_share = successes / total
    assert abs(ci["observedShare"] - expected_share) < 1e-10


@given(
    successes=st.integers(min_value=0, max_value=10000),
    total=st.integers(min_value=1, max_value=10000),
    confidence_level=_confidence_levels,
)
@settings(max_examples=100)
def test_sample_size_and_method(successes, total, confidence_level):
    """sampleSize equals total and method is always wilson-score."""
    assume(successes <= total)

    ci = wilson_score_interval(successes, total, confidence_level)

    assert ci["sampleSize"] == total
    assert ci["method"] == "wilson-score"
    assert ci["confidenceLevel"] == confidence_level


@given(confidence_level=_confidence_levels)
@settings(max_examples=100)
def test_zero_total_returns_zeros(confidence_level):
    """When total is 0, all values are 0."""
    ci = wilson_score_interval(0, 0, confidence_level)

    assert ci["lower"] == 0
    assert ci["upper"] == 0
    assert ci["observedShare"] == 0
    assert ci["sampleSize"] == 0
    assert ci["method"] == "wilson-score"


@given(
    total=st.integers(min_value=1, max_value=10000),
    confidence_level=_confidence_levels,
)
@settings(max_examples=100)
def test_all_successes_upper_bound_is_one(total, confidence_level):
    """When successes == total, upper bound should be clamped to 1."""
    ci = wilson_score_interval(total, total, confidence_level)

    assert ci["upper"] <= 1.0
    assert ci["observedShare"] == 1.0
