"""Feature: canonical-intent-engine, Property 18: Explainability fields present

For any InputRecord processed through the engine, the resulting
IntentDeterminationResult should have a non-empty decision_method field
(one of exact, synonym, pattern, protected, unsupported, unknown, or error)
and a non-empty applied_rules list.

**Validates: Requirements 12.1, 12.2**
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

VALID_DECISION_METHODS = {
    "exact",
    "synonym",
    "pattern",
    "protected",
    "unsupported",
    "unknown",
    "error",
}


def _make_test_config() -> IntentEngineConfig:
    """Build a fixed IntentEngineConfig for explainability tests."""
    return IntentEngineConfig(
        catalogVersion="explainability-test-v1",
        catalog=_CATALOG,
        protectedCase=ProtectedCaseConfig(
            policyBlockedPatterns=[r"\b(kill|attack)\b"],
            piiIndicators=[r"\b\d{3}-\d{2}-\d{4}\b"],
            nonEnglishPatterns=[r"[\u4e00-\u9fff]"],
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


# ─── Property 18: Explainability fields present ─────────────────────────────


@given(record=input_record_st())
@settings(max_examples=100)
def test_explainability_fields_present(record: InputRecord):
    """Feature: canonical-intent-engine, Property 18: Explainability fields present

    For any InputRecord processed through the engine, the resulting
    IntentDeterminationResult should have a non-empty decision_method field
    (one of exact, synonym, pattern, protected, unsupported, unknown, or error)
    and a non-empty applied_rules list.

    **Validates: Requirements 12.1, 12.2**
    """
    svc = IntentDeterminationService(TEST_CONFIG)
    result = svc.determine(record)

    # decision_method must be non-empty and one of the valid values
    assert result.decision_method is not None, "decision_method should not be None"
    assert result.decision_method != "", "decision_method should not be empty"
    assert result.decision_method in VALID_DECISION_METHODS, (
        f"decision_method {result.decision_method!r} is not one of {VALID_DECISION_METHODS}"
    )

    # applied_rules must be non-empty
    assert result.applied_rules is not None, "applied_rules should not be None"
    assert len(result.applied_rules) >= 1, (
        f"applied_rules should have at least one entry, got {result.applied_rules!r}"
    )
