"""Property 12: Actionability Classification Correctness

For any confidence interval, materiality threshold, minimum sample size, and
protected flag, the actionability classification should follow:
protected → protected-override; sample < min → insufficient-evidence;
lower CI >= threshold → action-ready; observed >= threshold but lower < threshold
→ monitor; else → insufficient-evidence.

**Validates: Requirements 6.3**
"""

from __future__ import annotations

# Feature: python-analysis-backend, Property 12: Actionability Classification Correctness

from hypothesis import given, settings, assume
from hypothesis import strategies as st

from engine.statistical_evaluation import classify_actionability

# ─── Strategies ──────────────────────────────────────────────────────────────

_threshold = st.floats(min_value=0.001, max_value=0.5, allow_nan=False, allow_infinity=False)
_min_sample = st.integers(min_value=1, max_value=10000)
_sample_size = st.integers(min_value=0, max_value=20000)
_share = st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)


def _ci(lower: float, upper: float, observed: float, sample_size: int, confidence: float = 0.95):
    return {
        "lower": lower,
        "upper": upper,
        "observedShare": observed,
        "sampleSize": sample_size,
        "confidenceLevel": confidence,
        "method": "wilson-score",
    }


# ─── Property Tests ─────────────────────────────────────────────────────────


@given(
    lower=_share,
    upper=_share,
    observed=_share,
    sample_size=_sample_size,
    threshold=_threshold,
    min_sample=_min_sample,
)
@settings(max_examples=100)
def test_protected_always_protected_override(
    lower, upper, observed, sample_size, threshold, min_sample
):
    """Protected flag always yields protected-override regardless of other values."""
    ci = _ci(lower, upper, observed, sample_size)
    result = classify_actionability(ci, threshold, min_sample, True)
    assert result == "protected-override"


@given(
    lower=_share,
    upper=_share,
    observed=_share,
    threshold=_threshold,
    min_sample=st.integers(min_value=100, max_value=10000),
)
@settings(max_examples=100)
def test_small_sample_insufficient_evidence(
    lower, upper, observed, threshold, min_sample
):
    """Sample size below minimum yields insufficient-evidence (when not protected)."""
    sample_size = min_sample - 1
    assume(sample_size >= 0)
    ci = _ci(lower, upper, observed, sample_size)
    result = classify_actionability(ci, threshold, min_sample, False)
    assert result == "insufficient-evidence"


@given(
    threshold=st.floats(min_value=0.01, max_value=0.3, allow_nan=False, allow_infinity=False),
    min_sample=st.integers(min_value=1, max_value=100),
    sample_size=st.integers(min_value=100, max_value=10000),
)
@settings(max_examples=100)
def test_lower_ci_above_threshold_is_action_ready(threshold, min_sample, sample_size):
    """When lower CI >= threshold and sample >= min, classification is action-ready."""
    assume(sample_size >= min_sample)
    lower = threshold + 0.01
    observed = lower + 0.05
    upper = min(1.0, observed + 0.1)

    ci = _ci(lower, upper, observed, sample_size)
    result = classify_actionability(ci, threshold, min_sample, False)
    assert result == "action-ready"


@given(
    threshold=st.floats(min_value=0.02, max_value=0.3, allow_nan=False, allow_infinity=False),
    min_sample=st.integers(min_value=1, max_value=100),
    sample_size=st.integers(min_value=100, max_value=10000),
)
@settings(max_examples=100)
def test_observed_above_lower_below_is_monitor(threshold, min_sample, sample_size):
    """When observed >= threshold but lower < threshold, classification is monitor."""
    assume(sample_size >= min_sample)
    lower = threshold - 0.01
    assume(lower >= 0)
    observed = threshold + 0.01
    upper = min(1.0, observed + 0.1)

    ci = _ci(lower, upper, observed, sample_size)
    result = classify_actionability(ci, threshold, min_sample, False)
    assert result == "monitor"


@given(
    threshold=st.floats(min_value=0.1, max_value=0.5, allow_nan=False, allow_infinity=False),
    min_sample=st.integers(min_value=1, max_value=100),
    sample_size=st.integers(min_value=100, max_value=10000),
)
@settings(max_examples=100)
def test_both_below_threshold_is_insufficient(threshold, min_sample, sample_size):
    """When both observed and lower are below threshold, classification is insufficient-evidence."""
    assume(sample_size >= min_sample)
    observed = threshold - 0.05
    assume(observed >= 0)
    lower = observed - 0.01
    assume(lower >= 0)
    upper = min(1.0, observed + 0.1)

    ci = _ci(lower, upper, observed, sample_size)
    result = classify_actionability(ci, threshold, min_sample, False)
    assert result == "insufficient-evidence"
