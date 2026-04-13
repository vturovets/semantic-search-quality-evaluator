"""Feature: canonical-intent-engine, Properties 19 & 20: Batch Processing

Property 19: Batch-single equivalence — For any list of InputRecords,
calling determine_batch(records) should produce results where each element
is identical to calling determine(record) individually for the corresponding
record.

Property 20: Batch error isolation — For any batch of InputRecords, the
batch always returns the same number of results as input records, and each
result contains all required fields regardless of other records in the batch.

**Validates: Requirements 13.3, 13.4, 14.2**
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


def _make_test_config() -> IntentEngineConfig:
    """Build a fixed IntentEngineConfig for batch processing tests."""
    return IntentEngineConfig(
        catalogVersion="batch-test-v1",
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


# ─── Property 19: Batch-single equivalence ──────────────────────────────────


@given(records=st.lists(input_record_st(), min_size=1, max_size=5))
@settings(max_examples=100)
def test_batch_single_equivalence(records: list[InputRecord]):
    """Feature: canonical-intent-engine, Property 19: Batch-single equivalence

    For any list of InputRecords, calling determine_batch(records) should
    produce results where each element is identical to calling determine(record)
    individually for the corresponding record.

    **Validates: Requirements 13.3, 14.2**
    """
    svc = IntentDeterminationService(TEST_CONFIG)

    batch_results = svc.determine_batch(records)
    individual_results = [svc.determine(record) for record in records]

    assert len(batch_results) == len(records), (
        f"Batch returned {len(batch_results)} results for {len(records)} records"
    )

    for i, (batch_r, individual_r) in enumerate(zip(batch_results, individual_results)):
        assert batch_r.source_id == individual_r.source_id, (
            f"Record {i}: source_id mismatch: {batch_r.source_id!r} != {individual_r.source_id!r}"
        )
        assert batch_r.canonical_intent_id == individual_r.canonical_intent_id, (
            f"Record {i}: canonical_intent_id mismatch: "
            f"{batch_r.canonical_intent_id!r} != {individual_r.canonical_intent_id!r}"
        )
        assert batch_r.canonical_intent_label == individual_r.canonical_intent_label, (
            f"Record {i}: canonical_intent_label mismatch: "
            f"{batch_r.canonical_intent_label!r} != {individual_r.canonical_intent_label!r}"
        )
        assert batch_r.intent_class == individual_r.intent_class, (
            f"Record {i}: intent_class mismatch: "
            f"{batch_r.intent_class!r} != {individual_r.intent_class!r}"
        )
        assert batch_r.protected_class == individual_r.protected_class, (
            f"Record {i}: protected_class mismatch: "
            f"{batch_r.protected_class!r} != {individual_r.protected_class!r}"
        )
        assert batch_r.normalized_status == individual_r.normalized_status, (
            f"Record {i}: normalized_status mismatch: "
            f"{batch_r.normalized_status!r} != {individual_r.normalized_status!r}"
        )
        assert batch_r.normalized_option_signature == individual_r.normalized_option_signature, (
            f"Record {i}: normalized_option_signature mismatch: "
            f"{batch_r.normalized_option_signature!r} != {individual_r.normalized_option_signature!r}"
        )
        assert batch_r.comparison_anchor == individual_r.comparison_anchor, (
            f"Record {i}: comparison_anchor mismatch: "
            f"{batch_r.comparison_anchor!r} != {individual_r.comparison_anchor!r}"
        )
        assert batch_r.decision_method == individual_r.decision_method, (
            f"Record {i}: decision_method mismatch: "
            f"{batch_r.decision_method!r} != {individual_r.decision_method!r}"
        )
        assert batch_r.applied_rules == individual_r.applied_rules, (
            f"Record {i}: applied_rules mismatch: "
            f"{batch_r.applied_rules!r} != {individual_r.applied_rules!r}"
        )
        assert batch_r.ambiguity_flag == individual_r.ambiguity_flag, (
            f"Record {i}: ambiguity_flag mismatch: "
            f"{batch_r.ambiguity_flag!r} != {individual_r.ambiguity_flag!r}"
        )
        assert batch_r.catalog_version == individual_r.catalog_version, (
            f"Record {i}: catalog_version mismatch: "
            f"{batch_r.catalog_version!r} != {individual_r.catalog_version!r}"
        )
        assert batch_r.sanitized_text == individual_r.sanitized_text, (
            f"Record {i}: sanitized_text mismatch: "
            f"{batch_r.sanitized_text!r} != {individual_r.sanitized_text!r}"
        )
        assert batch_r.error_message == individual_r.error_message, (
            f"Record {i}: error_message mismatch: "
            f"{batch_r.error_message!r} != {individual_r.error_message!r}"
        )

        # Full model equality as safety net
        assert batch_r == individual_r, (
            f"Record {i}: full model equality failed.\n"
            f"Batch:      {batch_r}\n"
            f"Individual: {individual_r}"
        )


# ─── Property 20: Batch error isolation ─────────────────────────────────────


@given(records=st.lists(input_record_st(), min_size=1, max_size=5))
@settings(max_examples=100)
def test_batch_error_isolation(records: list[InputRecord]):
    """Feature: canonical-intent-engine, Property 20: Batch error isolation

    For any batch of InputRecords, determine_batch always returns the same
    number of results as input records, and each result has all required
    fields populated. No single record's processing can prevent other
    records from being processed.

    **Validates: Requirements 13.4**
    """
    svc = IntentDeterminationService(TEST_CONFIG)

    results = svc.determine_batch(records)

    # Batch must return exactly one result per input record
    assert len(results) == len(records), (
        f"Batch returned {len(results)} results for {len(records)} records"
    )

    for i, result in enumerate(results):
        # Every result must have all required fields populated
        assert result.source_id is not None, (
            f"Record {i}: source_id is None"
        )
        assert result.intent_class in ("SUPPORTED", "UNSUPPORTED", "PROTECTED", "UNKNOWN"), (
            f"Record {i}: invalid intent_class: {result.intent_class!r}"
        )
        assert result.normalized_status is not None and result.normalized_status != "", (
            f"Record {i}: normalized_status is empty or None"
        )
        assert result.normalized_option_signature is not None, (
            f"Record {i}: normalized_option_signature is None"
        )
        assert result.comparison_anchor is not None and result.comparison_anchor != "", (
            f"Record {i}: comparison_anchor is empty or None"
        )
        assert result.decision_method is not None and result.decision_method != "", (
            f"Record {i}: decision_method is empty or None"
        )
        assert result.applied_rules is not None and len(result.applied_rules) > 0, (
            f"Record {i}: applied_rules is empty or None"
        )
        assert result.catalog_version == TEST_CONFIG.catalog_version, (
            f"Record {i}: catalog_version mismatch: "
            f"{result.catalog_version!r} != {TEST_CONFIG.catalog_version!r}"
        )
        assert result.sanitized_text is not None, (
            f"Record {i}: sanitized_text is None"
        )

        # source_id must correspond to the input record
        assert result.source_id == records[i].source_id, (
            f"Record {i}: source_id {result.source_id!r} does not match "
            f"input source_id {records[i].source_id!r}"
        )
