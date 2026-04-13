"""Feature: canonical-intent-engine — Outcome normalization property tests.

Property 12: Status normalization lookup
Property 13: Option normalization lookup

These tests verify that the normalize_outcome pipeline stage correctly maps
status and option values through their respective normalization configs,
falling back to UNDETERMINED for unmapped statuses and lowercased/trimmed
pass-through for unmapped options.
"""

from __future__ import annotations

from hypothesis import given, settings, assume
from hypothesis import strategies as st

from engine.intent_config import (
    CatalogEntry,
    IntentEngineConfig,
    NormalizationConfig,
    OptionNormalizationConfig,
    ProtectedCaseConfig,
    StatusNormalizationConfig,
)
from engine.intent_pipeline import PipelineState, normalize_outcome
from models.intent_models import InputRecord


# ─── Test Configuration ─────────────────────────────────────────────────────

CANONICAL_STATUSES = {
    "active": "MAPPED_AND_APPLIED",
    "partial": "PARTIALLY_APPLIED",
    "confirmed": "MAPPED_AND_APPLIED",
    "pending": "PARTIALLY_APPLIED",
}

CANONICAL_OPTIONS = {
    "all inclusive": "BOARDS:ALL_INCLUSIVE",
    "villa": "ACCOMMODATIONTYPE:VILLA",
    "half board": "BOARDS:HALF_BOARD",
    "apartment": "ACCOMMODATIONTYPE:APARTMENT",
}


def _make_test_config() -> IntentEngineConfig:
    """Build a minimal IntentEngineConfig for outcome normalization tests."""
    return IntentEngineConfig(
        catalogVersion="test-v1",
        catalog=[],
        protectedCase=ProtectedCaseConfig(
            policyBlockedPatterns=[],
            piiIndicators=[],
            nonEnglishPatterns=[],
            onMatch="terminate",
        ),
        normalization=NormalizationConfig(
            spellingVariants={},
            separatorReplacements={},
            punctuationStripPattern=r"[^\w\s]",
        ),
        statusNormalization=StatusNormalizationConfig(
            canonicalStatuses=CANONICAL_STATUSES,
            defaultUnmapped="UNDETERMINED",
        ),
        optionNormalization=OptionNormalizationConfig(
            canonicalOptions=CANONICAL_OPTIONS,
        ),
        disambiguationRules=[],
    )


TEST_CONFIG = _make_test_config()


# ─── Strategies ──────────────────────────────────────────────────────────────

_id_st = st.text(
    alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyz0123456789"),
    min_size=3,
    max_size=15,
)

_safe_text_st = st.text(
    alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyz0123456789 "),
    min_size=1,
    max_size=40,
).filter(lambda s: s.strip() != "")

# Status values that ARE in the canonical map
_mapped_status_st = st.sampled_from(list(CANONICAL_STATUSES.keys()))

# Status values that are NOT in the canonical map
_unmapped_status_st = st.text(
    alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyz"),
    min_size=3,
    max_size=20,
).filter(lambda s: s not in CANONICAL_STATUSES)

# Option values that ARE in the canonical map
_mapped_option_st = st.sampled_from(list(CANONICAL_OPTIONS.keys()))

# Option values that are NOT in the canonical map
_unmapped_option_st = st.text(
    alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ "),
    min_size=2,
    max_size=25,
).filter(lambda s: s.strip() != "" and s not in CANONICAL_OPTIONS)


def _make_supported_state(
    expected_status: str | None = None,
    expected_options: list[str] | None = None,
) -> PipelineState:
    """Build a PipelineState with intent_class=SUPPORTED and given expected values."""
    record = InputRecord(
        sourceType="REAL",
        sourceId="test-001",
        rawText="test input",
        sanitizedText="test input",
        expectedStatus=expected_status,
        expectedOptions=expected_options,
    )
    return PipelineState(
        record=record,
        normalized_text="test input",
        intent_class="SUPPORTED",
        canonical_intent_id="intent-001",
        canonical_intent_label="Test Intent",
        decision_method="exact",
    )


# ─── Property 12: Status normalization lookup ───────────────────────────────


@given(status=_mapped_status_st)
@settings(max_examples=100)
def test_mapped_status_normalizes_to_canonical_value(status: str):
    """Feature: canonical-intent-engine, Property 12: Status normalization lookup

    For any status value present in the StatusNormalizationConfig.canonical_statuses
    map, the normalized status in the result should equal the corresponding
    canonical value.

    **Validates: Requirements 5.1, 5.3**
    """
    state = _make_supported_state(expected_status=status)
    result = normalize_outcome(state, TEST_CONFIG)

    expected_canonical = CANONICAL_STATUSES[status]
    assert result.normalized_status == expected_canonical, (
        f"Status {status!r} should normalize to {expected_canonical!r}, "
        f"got {result.normalized_status!r}"
    )


@given(status=_unmapped_status_st)
@settings(max_examples=100)
def test_unmapped_status_normalizes_to_undetermined(status: str):
    """Feature: canonical-intent-engine, Property 12: Status normalization lookup

    For any status value NOT in the StatusNormalizationConfig.canonical_statuses
    map, the normalized status should be "UNDETERMINED" (the default_unmapped).

    **Validates: Requirements 5.1, 5.3**
    """
    state = _make_supported_state(expected_status=status)
    result = normalize_outcome(state, TEST_CONFIG)

    assert result.normalized_status == "UNDETERMINED", (
        f"Unmapped status {status!r} should normalize to 'UNDETERMINED', "
        f"got {result.normalized_status!r}"
    )


# ─── Property 13: Option normalization lookup ────────────────────────────────


@given(option=_mapped_option_st)
@settings(max_examples=100)
def test_mapped_option_normalizes_to_canonical_value(option: str):
    """Feature: canonical-intent-engine, Property 13: Option normalization lookup

    For any option value present in the OptionNormalizationConfig.canonical_options
    map, the normalized option should equal the corresponding canonical value.

    **Validates: Requirements 5.2, 5.4**
    """
    state = _make_supported_state(expected_options=[option])
    result = normalize_outcome(state, TEST_CONFIG)

    expected_canonical = CANONICAL_OPTIONS[option]
    assert result.normalized_option_signature == expected_canonical, (
        f"Option {option!r} should normalize to {expected_canonical!r}, "
        f"got {result.normalized_option_signature!r}"
    )


@given(option=_unmapped_option_st)
@settings(max_examples=100)
def test_unmapped_option_normalizes_to_lowercased_trimmed(option: str):
    """Feature: canonical-intent-engine, Property 13: Option normalization lookup

    For any option value NOT in the OptionNormalizationConfig.canonical_options
    map, the normalized option should be the lowercased, trimmed version.

    **Validates: Requirements 5.2, 5.4**
    """
    state = _make_supported_state(expected_options=[option])
    result = normalize_outcome(state, TEST_CONFIG)

    expected = option.strip().lower()
    assert result.normalized_option_signature == expected, (
        f"Unmapped option {option!r} should normalize to {expected!r}, "
        f"got {result.normalized_option_signature!r}"
    )


# ─── Property 14: Comparison anchor format per intent class ──────────────────

from engine.intent_pipeline import build_anchor


_protected_class_st = st.sampled_from([
    "REJECTED_BY_POLICY",
    "PII_DETECTED",
    "REJECTED_NON_ENGLISH",
])

_label_st = st.text(
    alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyz "),
    min_size=1,
    max_size=30,
).filter(lambda s: s.strip() != "")

_status_st = st.sampled_from([
    "MAPPED_AND_APPLIED",
    "PARTIALLY_APPLIED",
    "NO_VALID_MAPPING",
    "UNDETERMINED",
])

_option_sig_st = st.sampled_from([
    "BOARDS:ALL_INCLUSIVE",
    "ACCOMMODATIONTYPE:VILLA",
    "",
])


def _make_record(sanitized_text: str = "test input") -> InputRecord:
    """Build a minimal InputRecord for anchor tests."""
    return InputRecord(
        sourceType="REAL",
        sourceId="anchor-test",
        rawText=sanitized_text,
        sanitizedText=sanitized_text,
    )


@given(
    label=_label_st,
    status=_status_st,
    options=_option_sig_st,
)
@settings(max_examples=100)
def test_supported_anchor_format(label: str, status: str, options: str):
    """Feature: canonical-intent-engine, Property 14: Comparison anchor format per intent class

    For a SUPPORTED intent, the comparison anchor must be a pipe-delimited
    string with exactly 4 segments: SUPPORTED | <label> | <status> | <options>.

    **Validates: Requirements 6.1, 6.2**
    """
    state = PipelineState(
        record=_make_record(),
        normalized_text="test input",
        intent_class="SUPPORTED",
        canonical_intent_label=label,
        normalized_status=status,
        normalized_option_signature=options,
    )
    result = build_anchor(state, TEST_CONFIG)
    anchor = result.comparison_anchor

    segments = anchor.split(" | ")
    assert len(segments) == 4, f"SUPPORTED anchor should have 4 segments, got {len(segments)}: {anchor!r}"
    assert segments[0] == "SUPPORTED"
    assert segments[1] == label
    assert segments[2] == status
    assert segments[3] == options


@given(label=_label_st)
@settings(max_examples=100)
def test_unsupported_anchor_format(label: str):
    """Feature: canonical-intent-engine, Property 14: Comparison anchor format per intent class

    For an UNSUPPORTED intent, the comparison anchor must be a pipe-delimited
    string with exactly 3 segments: UNSUPPORTED | NO_VALID_MAPPING | <label>.

    **Validates: Requirements 6.1, 6.3**
    """
    state = PipelineState(
        record=_make_record(),
        normalized_text="test input",
        intent_class="UNSUPPORTED",
        canonical_intent_label=label,
        normalized_status="NO_VALID_MAPPING",
    )
    result = build_anchor(state, TEST_CONFIG)
    anchor = result.comparison_anchor

    segments = anchor.split(" | ")
    assert len(segments) == 3, f"UNSUPPORTED anchor should have 3 segments, got {len(segments)}: {anchor!r}"
    assert segments[0] == "UNSUPPORTED"
    assert segments[1] == "NO_VALID_MAPPING"
    assert segments[2] == label


@given(sanitized=_safe_text_st)
@settings(max_examples=100)
def test_unknown_anchor_format(sanitized: str):
    """Feature: canonical-intent-engine, Property 14: Comparison anchor format per intent class

    For an UNKNOWN intent, the comparison anchor must be a pipe-delimited
    string with exactly 3 segments: UNKNOWN | UNDETERMINED | <sanitized_text>.

    **Validates: Requirements 6.1, 6.4**
    """
    state = PipelineState(
        record=_make_record(sanitized_text=sanitized),
        normalized_text=sanitized.lower(),
        intent_class="UNKNOWN",
        normalized_status="UNDETERMINED",
    )
    result = build_anchor(state, TEST_CONFIG)
    anchor = result.comparison_anchor

    segments = anchor.split(" | ")
    assert len(segments) == 3, f"UNKNOWN anchor should have 3 segments, got {len(segments)}: {anchor!r}"
    assert segments[0] == "UNKNOWN"
    assert segments[1] == "UNDETERMINED"
    assert segments[2] == sanitized


@given(
    protected_class=_protected_class_st,
    sanitized=_safe_text_st,
)
@settings(max_examples=100)
def test_protected_anchor_format(protected_class: str, sanitized: str):
    """Feature: canonical-intent-engine, Property 14: Comparison anchor format per intent class

    For a PROTECTED intent, the comparison anchor must be a pipe-delimited
    string with exactly 3 segments: PROTECTED | <protected_class> | <sanitized_text>.

    **Validates: Requirements 6.1, 6.5**
    """
    state = PipelineState(
        record=_make_record(sanitized_text=sanitized),
        normalized_text=sanitized.lower(),
        intent_class="PROTECTED",
        protected_class=protected_class,
        protected_flag=True,
    )
    result = build_anchor(state, TEST_CONFIG)
    anchor = result.comparison_anchor

    segments = anchor.split(" | ")
    assert len(segments) == 3, f"PROTECTED anchor should have 3 segments, got {len(segments)}: {anchor!r}"
    assert segments[0] == "PROTECTED"
    assert segments[1] == protected_class
    assert segments[2] == sanitized
