"""Feature: canonical-intent-engine, Property 22: Result contains all required fields

For any IntentDeterminationResult, all specified fields are present:
canonical_intent_id, canonical_intent_label, intent_class, protected_class,
normalized_status, normalized_option_signature, comparison_anchor,
decision_method, applied_rules, ambiguity_flag, catalog_version, and
sanitized_text.

**Validates: Requirements 16.2**
"""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from models.enums import IntentClass
from models.intent_models import IntentDeterminationResult

# ─── Hypothesis Strategies ───────────────────────────────────────────────────

_nonempty_str = st.text(min_size=1, max_size=30).filter(lambda s: s.strip() != "")

_intent_class_st = st.sampled_from(["SUPPORTED", "UNSUPPORTED", "PROTECTED", "UNKNOWN"])

_protected_class_st = st.one_of(st.none(), _nonempty_str)


@st.composite
def intent_determination_result_st(draw):
    """Strategy for generating valid IntentDeterminationResult objects."""
    return IntentDeterminationResult(
        source_id=draw(_nonempty_str),
        canonical_intent_id=draw(st.one_of(st.none(), _nonempty_str)),
        canonical_intent_label=draw(st.one_of(st.none(), _nonempty_str)),
        intent_class=draw(_intent_class_st),
        protected_class=draw(_protected_class_st),
        normalized_status=draw(_nonempty_str),
        normalized_option_signature=draw(_nonempty_str),
        comparison_anchor=draw(_nonempty_str),
        decision_method=draw(_nonempty_str),
        applied_rules=draw(st.lists(_nonempty_str, min_size=0, max_size=5)),
        ambiguity_flag=draw(st.booleans()),
        catalog_version=draw(_nonempty_str),
        sanitized_text=draw(_nonempty_str),
        error_message=draw(st.one_of(st.none(), _nonempty_str)),
    )


# ─── All fields that must exist on the model ─────────────────────────────────

ALL_SPECIFIED_FIELDS = [
    "canonical_intent_id",
    "canonical_intent_label",
    "intent_class",
    "protected_class",
    "normalized_status",
    "normalized_option_signature",
    "comparison_anchor",
    "decision_method",
    "applied_rules",
    "ambiguity_flag",
    "catalog_version",
    "sanitized_text",
]

# Fields that must never be None (required by the model with no default of None)
REQUIRED_NON_NONE_FIELDS = [
    "intent_class",
    "normalized_status",
    "normalized_option_signature",
    "comparison_anchor",
    "decision_method",
    "applied_rules",
    "catalog_version",
    "sanitized_text",
]


# ─── Property Test ───────────────────────────────────────────────────────────


@given(result=intent_determination_result_st())
@settings(max_examples=100)
def test_result_contains_all_required_fields(result: IntentDeterminationResult):
    """Property 22: Every IntentDeterminationResult contains all specified fields
    and required fields are not None.

    **Validates: Requirements 16.2**
    """
    # All specified field names exist on the model
    for field_name in ALL_SPECIFIED_FIELDS:
        assert hasattr(result, field_name), (
            f"IntentDeterminationResult is missing field: {field_name}"
        )

    # Required fields are not None
    for field_name in REQUIRED_NON_NONE_FIELDS:
        assert getattr(result, field_name) is not None, (
            f"Required field '{field_name}' must not be None, got None"
        )


# ─── Additional imports for Properties 21 & 23 ──────────────────────────────

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


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _make_config(
    catalog_version: str,
    intent_id: str,
    intent_label: str,
    exact_phrase: str,
) -> IntentEngineConfig:
    """Build a minimal IntentEngineConfig with a single catalog entry."""
    return IntentEngineConfig(
        catalogVersion=catalog_version,
        catalog=[
            CatalogEntry(
                intentId=intent_id,
                intentLabel=intent_label,
                intentFamily="test-family",
                intentClass="SUPPORTED",
                exactPhrases=[exact_phrase],
                synonyms=[],
                patterns=[],
                priorityScore=10.0,
                protectedFlag=False,
            ),
        ],
        protectedCase=ProtectedCaseConfig(
            policyBlockedPatterns=[],
            piiIndicators=[],
            nonEnglishPatterns=[],
            onMatch="terminate",
        ),
        normalization=NormalizationConfig(
            spellingVariants={},
            separatorReplacements={"-": " ", "_": " "},
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


def _make_input_record(sanitized_text: str, source_id: str = "src-1") -> InputRecord:
    """Build a minimal InputRecord."""
    return InputRecord(
        sourceType="REAL",
        sourceId=source_id,
        rawText=sanitized_text,
        sanitizedText=sanitized_text,
    )


# ─── Strategies for Properties 21 & 23 ──────────────────────────────────────

_id_alpha = st.text(
    alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyz"),
    min_size=3,
    max_size=12,
)

_version_st = st.text(
    alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyz0123456789.-"),
    min_size=1,
    max_size=20,
).filter(lambda s: s.strip() != "")

_source_type_st = st.sampled_from(["REAL", "ACCURACY", "CONSISTENCY"])


@st.composite
def two_distinct_ids(draw):
    """Draw two distinct intent IDs and labels."""
    id_a = draw(_id_alpha)
    id_b = draw(_id_alpha.filter(lambda s: s != id_a))
    label_a = draw(_id_alpha)
    label_b = draw(_id_alpha.filter(lambda s: s != label_a))
    return id_a, label_a, id_b, label_b


# ─── Property 21: Config reload takes effect ────────────────────────────────


@given(data=two_distinct_ids())
@settings(max_examples=100)
def test_config_reload_takes_effect(data):
    """Property 21: Config reload takes effect

    For any IntentDeterminationService instance, after calling reload_config()
    with a new configuration, subsequent determine() calls should use the new
    configuration. We verify by creating config A with catalog entry X, then
    reloading with config B containing a different catalog entry Y for the same
    exact phrase, and confirming the result changes.

    **Validates: Requirements 15.4**
    """
    id_a, label_a, id_b, label_b = data
    exact_phrase = "test phrase"

    config_a = _make_config(
        catalog_version="v-a",
        intent_id=id_a,
        intent_label=label_a,
        exact_phrase=exact_phrase,
    )
    config_b = _make_config(
        catalog_version="v-b",
        intent_id=id_b,
        intent_label=label_b,
        exact_phrase=exact_phrase,
    )

    record = _make_input_record(exact_phrase)

    svc = IntentDeterminationService(config_a)

    # Before reload — should match entry from config A
    result_before = svc.determine(record)
    assert result_before.canonical_intent_id == id_a, (
        f"Before reload: expected intent_id {id_a!r}, got {result_before.canonical_intent_id!r}"
    )
    assert result_before.canonical_intent_label == label_a, (
        f"Before reload: expected label {label_a!r}, got {result_before.canonical_intent_label!r}"
    )

    # Reload with config B
    svc.reload_config(config_b)

    # After reload — should match entry from config B
    result_after = svc.determine(record)
    assert result_after.canonical_intent_id == id_b, (
        f"After reload: expected intent_id {id_b!r}, got {result_after.canonical_intent_id!r}"
    )
    assert result_after.canonical_intent_label == label_b, (
        f"After reload: expected label {label_b!r}, got {result_after.canonical_intent_label!r}"
    )

    # The two results should differ in intent identity
    assert result_before.canonical_intent_id != result_after.canonical_intent_id, (
        "Config reload did not take effect: intent_id is the same before and after reload"
    )


# ─── Property 23: Catalog version traceability ──────────────────────────────


@given(
    catalog_version=_version_st,
    source_type=_source_type_st,
    source_id=_id_alpha,
    sanitized_text=st.text(
        alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyz "),
        min_size=1,
        max_size=40,
    ).filter(lambda s: s.strip() != ""),
)
@settings(max_examples=100)
def test_catalog_version_traceability(
    catalog_version: str,
    source_type: str,
    source_id: str,
    sanitized_text: str,
):
    """Property 23: Catalog version traceability

    For any InputRecord processed through the engine, the catalog_version
    field in the IntentDeterminationResult should equal the catalog_version
    from the IntentEngineConfig used during processing.

    **Validates: Requirements 17.1, 17.3**
    """
    config = _make_config(
        catalog_version=catalog_version,
        intent_id="any-intent",
        intent_label="Any Intent",
        exact_phrase="will not match this phrase",
    )

    record = InputRecord(
        sourceType=source_type,
        sourceId=source_id,
        rawText=sanitized_text,
        sanitizedText=sanitized_text,
    )

    svc = IntentDeterminationService(config)
    result = svc.determine(record)

    assert result.catalog_version == catalog_version, (
        f"catalog_version mismatch: result has {result.catalog_version!r}, "
        f"config has {catalog_version!r}"
    )
