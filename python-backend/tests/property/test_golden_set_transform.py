"""Property 3: Golden-Set Header Transform Correctness

For any record with a combined options/status column value, the golden-set header
mapping transform should split it into separate expectedOptions (list) and
expectedStatus (string) fields, and the concatenation of the split parts should
reconstruct the original combined value.

**Validates: Requirements 3.5**
"""

from __future__ import annotations

from hypothesis import given, settings, assume
from hypothesis import strategies as st

from engine.parser import split_options_status, apply_golden_set_transform


# ─── Hypothesis Strategies ───────────────────────────────────────────────────

# Safe option text: no "; " to avoid ambiguity with the separator,
# no leading/trailing whitespace (since segments get trimmed),
# and must not start with "status:" (case-insensitive).
_option_text = st.text(
    alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:_-"),
    min_size=1,
    max_size=40,
).filter(
    lambda s: s.strip() == s
    and s.strip() != ""
    and "; " not in s
    and ";" not in s
    and not s.strip().lower().startswith("status:")
)

# Status values
_status_value = st.text(
    alphabet=st.sampled_from("ABCDEFGHIJKLMNOPQRSTUVWXYZ_"),
    min_size=1,
    max_size=20,
).filter(lambda s: s.strip() == s and s.strip() != "")


@st.composite
def _combined_options_status(draw):
    """Generate a combined options/status string with known structure."""
    has_status = draw(st.booleans())

    if has_status:
        n_options = draw(st.integers(min_value=1, max_value=3))
        options = [draw(_option_text) for _ in range(n_options)]
        status = draw(_status_value)
        combined = "; ".join(options) + "; Status: " + status
        return combined, options, status
    else:
        # Without a Status: segment, the entire value is returned as one option
        single_option = draw(_option_text)
        return single_option, [single_option], None


# ─── Property Tests ─────────────────────────────────────────────────────────
# Feature: python-analysis-backend, Property 3: Golden-Set Header Transform Correctness


@given(data=_combined_options_status())
@settings(max_examples=100)
def test_split_options_status_correctness(data):
    """Splitting a combined options/status string produces correct parts."""
    combined, expected_options, expected_status = data

    result = split_options_status(combined)

    assert result["expectedOptions"] == expected_options

    if expected_status is not None:
        assert result.get("expectedStatus") == expected_status
    else:
        assert "expectedStatus" not in result


@given(data=_combined_options_status())
@settings(max_examples=100)
def test_split_options_status_reconstruction(data):
    """The split parts can reconstruct the original combined value."""
    combined, _, _ = data

    result = split_options_status(combined)
    options = result["expectedOptions"]
    status = result.get("expectedStatus")

    if status is not None:
        reconstructed = "; ".join(options) + "; Status: " + status
    else:
        # When there's no status, the original is the joined options
        # But if there was only one option, it's the full trimmed string
        if len(options) == 1:
            reconstructed = options[0]
        else:
            reconstructed = "; ".join(options)

    assert reconstructed == combined.strip()


def test_split_empty_string():
    """Empty string produces empty options list."""
    result = split_options_status("")
    assert result == {"expectedOptions": []}


@given(
    test_case_id=st.text(
        alphabet=st.sampled_from("0123456789"),
        min_size=1,
        max_size=5,
    ),
    scenario=st.text(
        alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyz "),
        min_size=1,
        max_size=20,
    ).filter(lambda s: s.strip() != ""),
)
@settings(max_examples=100)
def test_apply_golden_set_transform_defaults(test_case_id, scenario):
    """Transform injects canonicalIntent from scenario and goldenSetVersion='1.0' when missing."""
    record = {
        "Test Case#": test_case_id,
        "Business requirement": "BR-1",
        "Scenario": scenario,
        "Free-text input": "some input",
        "Expected options, status": "Option: Value; Status: ACTIVE",
    }

    transformed = apply_golden_set_transform(record, "accuracy-golden-set")

    # Header mapping applied
    assert "testCaseId" in transformed
    assert transformed["testCaseId"] == test_case_id

    # canonicalIntent defaults to scenario
    assert transformed["canonicalIntent"] == scenario

    # goldenSetVersion defaults to '1.0'
    assert transformed["goldenSetVersion"] == "1.0"

    # Combined column split
    assert "expectedOptions" in transformed
    assert "expectedStatus" in transformed
    assert "_combinedOptionsStatus" not in transformed
