"""Property 10: Intent Classification Determinism

For any intent with given real count, golden count, real share, golden share,
protected flag, and materiality threshold, the classifyIntent function should
produce the same classification as the TypeScript reference implementation.

**Validates: Requirements 5.3, 5.4**
"""

from __future__ import annotations

# Feature: python-analysis-backend, Property 10: Intent Classification Determinism

from hypothesis import given, settings, assume
from hypothesis import strategies as st

from engine.comparison import classify_intent

# ─── Strategies ──────────────────────────────────────────────────────────────

_count = st.integers(min_value=0, max_value=1000)
_share = st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
_threshold = st.floats(min_value=0.001, max_value=0.5, allow_nan=False, allow_infinity=False)


# ─── Property Tests ─────────────────────────────────────────────────────────


@given(
    golden_count=st.integers(min_value=1, max_value=1000),
    golden_share=_share,
    threshold=_threshold,
)
@settings(max_examples=100)
def test_protected_with_golden_no_real_is_protected_retained(
    golden_count, golden_share, threshold
):
    """Protected intent with golden > 0 and real = 0 yields protected-retained."""
    result = classify_intent(0, golden_count, 0.0, golden_share, True, threshold)
    assert result == "protected-retained"


@given(
    real_count=st.integers(min_value=1, max_value=1000),
    real_share=_share,
    threshold=_threshold,
)
@settings(max_examples=100)
def test_real_only_when_golden_zero(real_count, real_share, threshold):
    """Real > 0 and golden = 0 yields real-only (regardless of protected flag)."""
    result = classify_intent(real_count, 0, real_share, 0.0, False, threshold)
    assert result == "real-only"

    # Also true when protected
    result_protected = classify_intent(real_count, 0, real_share, 0.0, True, threshold)
    assert result_protected == "real-only"


@given(
    golden_count=st.integers(min_value=1, max_value=1000),
    golden_share=_share,
    threshold=_threshold,
)
@settings(max_examples=100)
def test_candidate_obsolete_when_not_protected(golden_count, golden_share, threshold):
    """Real = 0 and golden > 0 (not protected) yields candidate-obsolete."""
    result = classify_intent(0, golden_count, 0.0, golden_share, False, threshold)
    assert result == "candidate-obsolete"


@given(
    real_count=st.integers(min_value=1, max_value=1000),
    golden_count=st.integers(min_value=1, max_value=1000),
    share=st.floats(min_value=0.01, max_value=0.99, allow_nan=False, allow_infinity=False),
    threshold=_threshold,
)
@settings(max_examples=100)
def test_matched_when_delta_within_threshold(real_count, golden_count, share, threshold):
    """When both counts > 0 and delta is within threshold, classification is matched."""
    # Use same share for both to ensure delta < threshold
    result = classify_intent(real_count, golden_count, share, share, False, threshold)
    assert result == "matched"


@given(
    real_count=st.integers(min_value=1, max_value=1000),
    golden_count=st.integers(min_value=1, max_value=1000),
    threshold=st.floats(min_value=0.001, max_value=0.1, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=100)
def test_underrepresented_when_positive_delta(real_count, golden_count, threshold):
    """When real share exceeds golden share by more than threshold, classification is underrepresented."""
    real_share = 0.8
    golden_share = 0.1
    assume(abs(real_share - golden_share) >= threshold)

    result = classify_intent(real_count, golden_count, real_share, golden_share, False, threshold)
    assert result == "underrepresented"


@given(
    real_count=st.integers(min_value=1, max_value=1000),
    golden_count=st.integers(min_value=1, max_value=1000),
    threshold=st.floats(min_value=0.001, max_value=0.1, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=100)
def test_overrepresented_when_negative_delta(real_count, golden_count, threshold):
    """When golden share exceeds real share by more than threshold, classification is overrepresented."""
    real_share = 0.1
    golden_share = 0.8
    assume(abs(real_share - golden_share) >= threshold)

    result = classify_intent(real_count, golden_count, real_share, golden_share, False, threshold)
    assert result == "overrepresented"


@given(threshold=_threshold)
@settings(max_examples=100)
def test_both_zero_yields_matched(threshold):
    """When both real and golden counts are 0, classification is matched (fallback)."""
    result = classify_intent(0, 0, 0.0, 0.0, False, threshold)
    assert result == "matched"


# ═══════════════════════════════════════════════════════════════════════════
# Feature: canonical-intent-engine
# Property 15: Unsupported intent invariants
# Property 16: Unknown handling invariants
# ═══════════════════════════════════════════════════════════════════════════

import re as _re

from engine.intent_config import (
    CatalogEntry,
    IntentEngineConfig,
    NormalizationConfig,
    OptionNormalizationConfig,
    ProtectedCaseConfig,
    StatusNormalizationConfig,
)
from engine.intent_pipeline import PipelineState, detect_unsupported, handle_unknown
from models.intent_models import InputRecord as _InputRecord

# ─── Helpers ─────────────────────────────────────────────────────────────────

_ie_id_st = st.text(
    alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyz0123456789"),
    min_size=3,
    max_size=15,
)

_ie_label_st = st.text(
    alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyz "),
    min_size=3,
    max_size=20,
).filter(lambda s: s.strip() != "")

_ie_phrase_st = st.text(
    alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyz "),
    min_size=3,
    max_size=30,
).map(lambda s: " ".join(s.split())).filter(lambda s: len(s) >= 3)

_ie_source_type_st = st.sampled_from(["REAL", "ACCURACY", "CONSISTENCY"])


def _ie_minimal_config(catalog=None):
    """Build a minimal IntentEngineConfig for classification tests."""
    return IntentEngineConfig(
        catalogVersion="test-v1",
        catalog=catalog or [],
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
            canonicalStatuses={},
            defaultUnmapped="UNDETERMINED",
        ),
        optionNormalization=OptionNormalizationConfig(
            canonicalOptions={},
        ),
        disambiguationRules=[],
    )


def _ie_minimal_record(sanitized_text="test input"):
    """Build a minimal InputRecord for pipeline state construction."""
    return _InputRecord(
        sourceType="REAL",
        sourceId="test-001",
        rawText=sanitized_text,
        sanitizedText=sanitized_text,
    )


# ─── Property 15: Unsupported intent invariants ─────────────────────────────


@st.composite
def unsupported_catalog_entry_with_matching_text_st(draw):
    """Generate an UNSUPPORTED CatalogEntry and a text that matches its exact_phrases."""
    intent_id = draw(_ie_id_st)
    label = draw(_ie_label_st)
    phrase = draw(_ie_phrase_st)

    entry = CatalogEntry(
        intentId=intent_id,
        intentLabel=label,
        intentFamily="general",
        intentClass="UNSUPPORTED",
        exactPhrases=[phrase],
        synonyms=[],
        patterns=[],
        priorityScore=1.0,
        protectedFlag=False,
    )
    return entry, phrase


@given(data=unsupported_catalog_entry_with_matching_text_st())
@settings(max_examples=100)
def test_unsupported_with_catalog_match(data):
    """Feature: canonical-intent-engine, Property 15: Unsupported intent invariants (catalog match)

    For any InputRecord classified as UNSUPPORTED via a matching catalog entry,
    the result should have normalized_status='NO_VALID_MAPPING' and the
    canonical unsupported label from the catalog assigned.

    **Validates: Requirements 7.1, 7.2, 7.3, 7.4**
    """
    entry, phrase = data

    config = _ie_minimal_config(catalog=[entry])
    record = _ie_minimal_record(sanitized_text=phrase)
    state = PipelineState(
        record=record,
        normalized_text=phrase,
        # No intent_class set, no matched_candidates — simulates no supported match
    )

    result = detect_unsupported(state, config)

    # Should be classified as UNSUPPORTED
    assert result.intent_class == "UNSUPPORTED", (
        f"Expected intent_class='UNSUPPORTED', got {result.intent_class!r}"
    )

    # normalized_status must be NO_VALID_MAPPING (Req 7.4)
    assert result.normalized_status == "NO_VALID_MAPPING", (
        f"Expected normalized_status='NO_VALID_MAPPING', got {result.normalized_status!r}"
    )

    # Should have the catalog entry's label (Req 7.2)
    assert result.canonical_intent_label == entry.intent_label, (
        f"Expected canonical_intent_label={entry.intent_label!r}, "
        f"got {result.canonical_intent_label!r}"
    )

    # Should have the catalog entry's intent_id
    assert result.canonical_intent_id == entry.intent_id, (
        f"Expected canonical_intent_id={entry.intent_id!r}, "
        f"got {result.canonical_intent_id!r}"
    )

    # Decision trace should record the unsupported entry
    assert any(
        f"unsupported:{entry.intent_id}" in rule for rule in result.applied_rules
    ), (
        f"Expected 'unsupported:{entry.intent_id}' in applied_rules, "
        f"got {result.applied_rules}"
    )


@given(
    normalized_text=_ie_phrase_st,
    source_type=_ie_source_type_st,
    source_id=_ie_id_st,
)
@settings(max_examples=100)
def test_unsupported_generic_when_no_catalog_match(normalized_text, source_type, source_id):
    """Feature: canonical-intent-engine, Property 15: Unsupported intent invariants (generic)

    For any InputRecord with no matching UNSUPPORTED catalog entry, the result
    should have normalized_status='NO_VALID_MAPPING', a generic unsupported
    label ('GENERIC_UNSUPPORTED'), and the normalized text in the decision trace.

    **Validates: Requirements 7.1, 7.2, 7.3, 7.4**
    """
    # Config with no UNSUPPORTED catalog entries
    config = _ie_minimal_config(catalog=[])
    record = _InputRecord(
        sourceType=source_type,
        sourceId=source_id,
        rawText=normalized_text,
        sanitizedText=normalized_text,
    )
    state = PipelineState(
        record=record,
        normalized_text=normalized_text,
        # No intent_class set, no matched_candidates
    )

    result = detect_unsupported(state, config)

    # Should be classified as UNSUPPORTED
    assert result.intent_class == "UNSUPPORTED", (
        f"Expected intent_class='UNSUPPORTED', got {result.intent_class!r}"
    )

    # normalized_status must be NO_VALID_MAPPING (Req 7.4)
    assert result.normalized_status == "NO_VALID_MAPPING", (
        f"Expected normalized_status='NO_VALID_MAPPING', got {result.normalized_status!r}"
    )

    # Generic unsupported label (Req 7.3)
    assert result.canonical_intent_label == "GENERIC_UNSUPPORTED", (
        f"Expected canonical_intent_label='GENERIC_UNSUPPORTED', "
        f"got {result.canonical_intent_label!r}"
    )

    # Normalized text should be in the decision trace (Req 7.3)
    assert normalized_text in result.applied_rules, (
        f"Expected normalized text {normalized_text!r} in applied_rules, "
        f"got {result.applied_rules}"
    )


# ─── Property 16: Unknown handling invariants ────────────────────────────────


@given(
    sanitized_text=_ie_phrase_st,
    source_type=_ie_source_type_st,
    source_id=_ie_id_st,
)
@settings(max_examples=100)
def test_unknown_handling_invariants(sanitized_text, source_type, source_id):
    """Feature: canonical-intent-engine, Property 16: Unknown handling invariants

    For any InputRecord classified as UNKNOWN, the result should have
    normalized_status='UNDETERMINED' and the sanitized_text field should
    contain the original sanitized text from the InputRecord.

    **Validates: Requirements 8.1, 8.2, 8.4, 8.5**
    """
    config = _ie_minimal_config()
    record = _InputRecord(
        sourceType=source_type,
        sourceId=source_id,
        rawText=sanitized_text,
        sanitizedText=sanitized_text,
    )
    state = PipelineState(
        record=record,
        normalized_text=sanitized_text,
        # No intent_class set, no matched_candidates — triggers unknown
    )

    result = handle_unknown(state, config)

    # Should be classified as UNKNOWN (Req 8.1)
    assert result.intent_class == "UNKNOWN", (
        f"Expected intent_class='UNKNOWN', got {result.intent_class!r}"
    )

    # normalized_status must be UNDETERMINED (Req 8.4)
    assert result.normalized_status == "UNDETERMINED", (
        f"Expected normalized_status='UNDETERMINED', got {result.normalized_status!r}"
    )

    # decision_method should be 'unknown'
    assert result.decision_method == "unknown", (
        f"Expected decision_method='unknown', got {result.decision_method!r}"
    )

    # The original sanitized_text is preserved on the record (Req 8.5)
    assert result.record.sanitized_text == sanitized_text, (
        f"Expected record.sanitized_text={sanitized_text!r}, "
        f"got {result.record.sanitized_text!r}"
    )

    # applied_rules should contain the reason tag
    assert any("unknown:" in rule for rule in result.applied_rules), (
        f"Expected 'unknown:' reason tag in applied_rules, got {result.applied_rules}"
    )


@given(
    sanitized_text=_ie_phrase_st,
    source_type=_ie_source_type_st,
    source_id=_ie_id_st,
)
@settings(max_examples=100)
def test_unknown_handling_with_ambiguity_flag(sanitized_text, source_type, source_id):
    """Feature: canonical-intent-engine, Property 16: Unknown handling with ambiguity

    For any InputRecord where ambiguity_flag is True and no intent_class was
    forced, handle_unknown should classify as UNKNOWN with
    normalized_status='UNDETERMINED' and preserve the sanitized_text.

    **Validates: Requirements 8.1, 8.2, 8.4, 8.5**
    """
    config = _ie_minimal_config()
    record = _InputRecord(
        sourceType=source_type,
        sourceId=source_id,
        rawText=sanitized_text,
        sanitizedText=sanitized_text,
    )
    state = PipelineState(
        record=record,
        normalized_text=sanitized_text,
        ambiguity_flag=True,
        # No intent_class set — ambiguity was unresolved
    )

    result = handle_unknown(state, config)

    # Should be classified as UNKNOWN
    assert result.intent_class == "UNKNOWN", (
        f"Expected intent_class='UNKNOWN', got {result.intent_class!r}"
    )

    # normalized_status must be UNDETERMINED
    assert result.normalized_status == "UNDETERMINED", (
        f"Expected normalized_status='UNDETERMINED', got {result.normalized_status!r}"
    )

    # The original sanitized_text is preserved on the record
    assert result.record.sanitized_text == sanitized_text, (
        f"Expected record.sanitized_text={sanitized_text!r}, "
        f"got {result.record.sanitized_text!r}"
    )

    # applied_rules should contain the ambiguous reason tag
    assert "unknown:ambiguous" in result.applied_rules, (
        f"Expected 'unknown:ambiguous' in applied_rules, got {result.applied_rules}"
    )
