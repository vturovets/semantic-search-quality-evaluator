"""Feature: canonical-intent-engine, Property 17: Determinism

For any InputRecord and IntentEngineConfig, calling determine() twice with
the same inputs should produce identical IntentDeterminationResult objects
(field-by-field equality).

**Validates: Requirements 11.1, 17.2**
"""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from engine.intent_config import (
    CatalogEntry,
    IntentEngineConfig,
    NormalizationConfig,
    OptionNormalizationConfig,
    ProtectedCaseConfig,
    StatusNormalizationConfig,
)
from engine.intent_engine import IntentDeterminationService
from models.intent_models import InputRecord


# ─── Test Configuration ─────────────────────────────────────────────────────

# A fixed config with a few catalog entries so that some inputs will match
# (exact, synonym, pattern) and some won't, exercising different code paths.

_CATALOG = [
    CatalogEntry(
        intentId="intent-booking",
        intentLabel="Booking Inquiry",
        intentFamily="reservations",
        intentClass="SUPPORTED",
        exactPhrases=["book a room", "make a reservation"],
        synonyms=["reserve a room", "get a booking"],
        patterns=[r"\b(book|reserve)\b.*\b(hotel|room|flight)\b"],
        priorityScore=10.0,
        protectedFlag=False,
    ),
    CatalogEntry(
        intentId="intent-cancel",
        intentLabel="Cancellation Request",
        intentFamily="reservations",
        intentClass="SUPPORTED",
        exactPhrases=["cancel my booking", "cancel reservation"],
        synonyms=["undo booking", "revoke reservation"],
        patterns=[r"\bcancel\b.*\b(booking|reservation|order)\b"],
        priorityScore=8.0,
        protectedFlag=False,
    ),
    CatalogEntry(
        intentId="intent-unsupported-complaint",
        intentLabel="General Complaint",
        intentFamily="feedback",
        intentClass="UNSUPPORTED",
        exactPhrases=["i want to complain", "file a complaint"],
        synonyms=["make a complaint"],
        patterns=[],
        priorityScore=1.0,
        protectedFlag=False,
    ),
]


def _make_test_config() -> IntentEngineConfig:
    """Build a fixed IntentEngineConfig with catalog entries for determinism tests."""
    return IntentEngineConfig(
        catalogVersion="determinism-test-v1",
        catalog=_CATALOG,
        protectedCase=ProtectedCaseConfig(
            policyBlockedPatterns=[r"\b(kill|attack)\b"],
            piiIndicators=[r"\b\d{3}-\d{2}-\d{4}\b"],  # SSN-like pattern
            nonEnglishPatterns=[r"[\u4e00-\u9fff]"],  # CJK characters
            onMatch="terminate",
        ),
        normalization=NormalizationConfig(
            spellingVariants={"colour": "color", "favourite": "favorite"},
            separatorReplacements={"-": " ", "_": " "},
            punctuationStripPattern=r"[^\w\s]",
        ),
        statusNormalization=StatusNormalizationConfig(
            canonicalStatuses={
                "active": "MAPPED_AND_APPLIED",
                "partial": "PARTIALLY_APPLIED",
            },
            defaultUnmapped="UNDETERMINED",
        ),
        optionNormalization=OptionNormalizationConfig(
            canonicalOptions={
                "all inclusive": "BOARDS:ALL_INCLUSIVE",
                "half board": "BOARDS:HALF_BOARD",
            },
        ),
        disambiguationRules=[],
    )


TEST_CONFIG = _make_test_config()


# ─── Strategies ──────────────────────────────────────────────────────────────

_source_type_st = st.sampled_from(["REAL", "ACCURACY", "CONSISTENCY"])

_id_st = st.text(
    alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyz0123456789"),
    min_size=3,
    max_size=15,
)

# Mix of texts that will hit different pipeline paths:
# - exact matches, synonym matches, pattern matches
# - protected-case triggers
# - unknown / unmatched inputs
_matching_texts = [
    "book a room",
    "make a reservation",
    "reserve a room",
    "get a booking",
    "cancel my booking",
    "undo booking",
    "i want to complain",
    "book a hotel for friday",
    "cancel the order please",
]

_protected_texts = [
    "i will kill you",
    "my ssn is 123-45-6789",
]

_unknown_texts = [
    "hello",
    "xyz",
    "what is the weather",
    "random gibberish text here",
]

_fixed_text_st = st.sampled_from(_matching_texts + _protected_texts + _unknown_texts)

_random_text_st = st.text(
    alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyz0123456789 "),
    min_size=1,
    max_size=60,
).filter(lambda s: s.strip() != "")

# Combine fixed known-path texts with random texts for broad coverage
_sanitized_text_st = st.one_of(_fixed_text_st, _random_text_st)

_optional_status_st = st.one_of(
    st.none(),
    st.sampled_from(["active", "partial", "unknown_status"]),
)

_optional_options_st = st.one_of(
    st.none(),
    st.lists(
        st.sampled_from(["all inclusive", "half board", "some random option"]),
        min_size=0,
        max_size=2,
    ),
)


@st.composite
def input_record_st(draw):
    """Generate a random InputRecord exercising various pipeline paths."""
    sanitized = draw(_sanitized_text_st)
    return InputRecord(
        sourceType=draw(_source_type_st),
        sourceId=draw(_id_st),
        rawText=sanitized,
        sanitizedText=sanitized,
        expectedStatus=draw(_optional_status_st),
        expectedOptions=draw(_optional_options_st),
    )


# ─── Property 17: Determinism ───────────────────────────────────────────────


@given(record=input_record_st())
@settings(max_examples=100)
def test_determine_is_deterministic(record: InputRecord):
    """Feature: canonical-intent-engine, Property 17: Determinism

    For any InputRecord and IntentEngineConfig, calling determine() twice
    with the same inputs should produce identical IntentDeterminationResult
    objects (field-by-field equality).

    **Validates: Requirements 11.1, 17.2**
    """
    svc = IntentDeterminationService(TEST_CONFIG)

    result1 = svc.determine(record)
    result2 = svc.determine(record)

    # Field-by-field equality check
    assert result1.source_id == result2.source_id, (
        f"source_id mismatch: {result1.source_id!r} != {result2.source_id!r}"
    )
    assert result1.canonical_intent_id == result2.canonical_intent_id, (
        f"canonical_intent_id mismatch: {result1.canonical_intent_id!r} != {result2.canonical_intent_id!r}"
    )
    assert result1.canonical_intent_label == result2.canonical_intent_label, (
        f"canonical_intent_label mismatch: {result1.canonical_intent_label!r} != {result2.canonical_intent_label!r}"
    )
    assert result1.intent_class == result2.intent_class, (
        f"intent_class mismatch: {result1.intent_class!r} != {result2.intent_class!r}"
    )
    assert result1.protected_class == result2.protected_class, (
        f"protected_class mismatch: {result1.protected_class!r} != {result2.protected_class!r}"
    )
    assert result1.normalized_status == result2.normalized_status, (
        f"normalized_status mismatch: {result1.normalized_status!r} != {result2.normalized_status!r}"
    )
    assert result1.normalized_option_signature == result2.normalized_option_signature, (
        f"normalized_option_signature mismatch: "
        f"{result1.normalized_option_signature!r} != {result2.normalized_option_signature!r}"
    )
    assert result1.comparison_anchor == result2.comparison_anchor, (
        f"comparison_anchor mismatch: {result1.comparison_anchor!r} != {result2.comparison_anchor!r}"
    )
    assert result1.decision_method == result2.decision_method, (
        f"decision_method mismatch: {result1.decision_method!r} != {result2.decision_method!r}"
    )
    assert result1.applied_rules == result2.applied_rules, (
        f"applied_rules mismatch: {result1.applied_rules!r} != {result2.applied_rules!r}"
    )
    assert result1.ambiguity_flag == result2.ambiguity_flag, (
        f"ambiguity_flag mismatch: {result1.ambiguity_flag!r} != {result2.ambiguity_flag!r}"
    )
    assert result1.catalog_version == result2.catalog_version, (
        f"catalog_version mismatch: {result1.catalog_version!r} != {result2.catalog_version!r}"
    )
    assert result1.sanitized_text == result2.sanitized_text, (
        f"sanitized_text mismatch: {result1.sanitized_text!r} != {result2.sanitized_text!r}"
    )
    assert result1.error_message == result2.error_message, (
        f"error_message mismatch: {result1.error_message!r} != {result2.error_message!r}"
    )

    # Also verify full model equality as a safety net
    assert result1 == result2, (
        f"Full model equality failed.\nResult 1: {result1}\nResult 2: {result2}"
    )
