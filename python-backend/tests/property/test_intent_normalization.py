"""Feature: canonical-intent-engine — Text normalization property tests.

Property 1: Text normalization transforms
Property 2: Normalization does not mutate original record
Property 3: Spelling variant round-trip lookup

These tests verify that the normalize_text pipeline stage correctly
lowercases, strips punctuation, replaces separators, and applies spelling
variants — all without mutating the original InputRecord.
"""

from __future__ import annotations

import copy
import re

from hypothesis import given, settings, assume
from hypothesis import strategies as st

from engine.intent_config import (
    CatalogEntry,
    DisambiguationRule,
    IntentEngineConfig,
    NormalizationConfig,
    OptionNormalizationConfig,
    ProtectedCaseConfig,
    StatusNormalizationConfig,
)
from engine.intent_pipeline import PipelineState, normalize_text
from models.intent_models import InputRecord


# ─── Test Configuration ─────────────────────────────────────────────────────

# A known, fixed test configuration used across all three properties.
SPELLING_VARIANTS = {
    "all-inclusive": "all inclusive",
    "wi-fi": "wifi",
    "e-mail": "email",
    "check-in": "checkin",
}

SEPARATOR_REPLACEMENTS = {
    "-": " ",
    "_": " ",
}

PUNCTUATION_STRIP_PATTERN = r"[!?.,;:\"'()\[\]{}]"


def _make_test_config() -> IntentEngineConfig:
    """Build a minimal IntentEngineConfig suitable for normalization tests."""
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
            spellingVariants=SPELLING_VARIANTS,
            separatorReplacements=SEPARATOR_REPLACEMENTS,
            punctuationStripPattern=PUNCTUATION_STRIP_PATTERN,
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


TEST_CONFIG = _make_test_config()


# ─── Strategies ──────────────────────────────────────────────────────────────

# Generate printable text that may include punctuation, separators, mixed case,
# and spelling variant keys — exercising every normalization path.
_safe_alphabet = st.sampled_from(
    list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -_!?.,;:'\"()[]{}") 
)

_sanitized_text_st = st.text(
    alphabet=_safe_alphabet,
    min_size=1,
    max_size=80,
).filter(lambda s: s.strip() != "")

_source_type_st = st.sampled_from(["REAL", "ACCURACY", "CONSISTENCY"])

_id_st = st.text(
    alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyz0123456789"),
    min_size=3,
    max_size=15,
)


@st.composite
def input_record_st(draw):
    """Generate a valid InputRecord with arbitrary sanitized_text."""
    return InputRecord(
        sourceType=draw(_source_type_st),
        sourceId=draw(_id_st),
        rawText=draw(_sanitized_text_st),
        sanitizedText=draw(_sanitized_text_st),
    )


# ─── Property 1: Text normalization transforms ──────────────────────────────


@given(record=input_record_st())
@settings(max_examples=100)
def test_text_normalization_transforms(record: InputRecord):
    """Feature: canonical-intent-engine, Property 1: Text normalization transforms

    For any InputRecord with arbitrary sanitized_text, after normalize_text the
    resulting normalized_text should be entirely lowercase, contain no raw
    punctuation (per the configured strip pattern), have all separator characters
    replaced, and all configured spelling variants replaced.

    **Validates: Requirements 1.1, 1.2, 1.3, 1.4**
    """
    state = PipelineState(record=record)
    result = normalize_text(state, TEST_CONFIG)
    text = result.normalized_text

    # Req 1.1 — entirely lowercase
    assert text == text.lower(), (
        f"normalized_text is not fully lowercase: {text!r}"
    )

    # Req 1.2 — no raw punctuation characters remain
    # The strip pattern replaces punctuation with spaces; after collapsing
    # whitespace, none of the stripped characters should survive.
    stripped_chars = set(re.findall(PUNCTUATION_STRIP_PATTERN, text))
    assert stripped_chars == set(), (
        f"Punctuation characters still present after normalization: {stripped_chars}"
    )

    # Req 1.3 — separator characters replaced (no hyphens or underscores)
    for sep in SEPARATOR_REPLACEMENTS:
        assert sep not in text, (
            f"Separator {sep!r} still present in normalized_text: {text!r}"
        )

    # Req 1.4 — spelling variants replaced
    for variant, canonical in SPELLING_VARIANTS.items():
        assert variant not in text, (
            f"Spelling variant {variant!r} still present in normalized_text: {text!r}"
        )


# ─── Property 2: Normalization does not mutate original record ───────────────


@given(record=input_record_st())
@settings(max_examples=100)
def test_normalization_does_not_mutate_original_record(record: InputRecord):
    """Feature: canonical-intent-engine, Property 2: Normalization does not mutate original record

    For any InputRecord, after running normalize_text, the original InputRecord's
    sanitized_text, raw_text, and all other fields should be identical to their
    values before processing.

    **Validates: Requirements 1.5**
    """
    # Deep copy before processing so we have a pristine reference
    original = copy.deepcopy(record)

    state = PipelineState(record=record)
    _ = normalize_text(state, TEST_CONFIG)

    # Every field on the original record must be unchanged
    assert record.source_type == original.source_type
    assert record.source_id == original.source_id
    assert record.raw_text == original.raw_text
    assert record.sanitized_text == original.sanitized_text
    assert record.source_group_id == original.source_group_id
    assert record.observed_at == original.observed_at
    assert record.expected_status == original.expected_status
    assert record.expected_options == original.expected_options


# ─── Property 3: Spelling variant round-trip lookup ──────────────────────────


@given(
    variant_key=st.sampled_from(list(SPELLING_VARIANTS.keys())),
    prefix=st.text(
        alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyz "),
        min_size=0,
        max_size=20,
    ),
    suffix=st.text(
        alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyz "),
        min_size=0,
        max_size=20,
    ),
)
@settings(max_examples=100)
def test_spelling_variant_round_trip_lookup(variant_key: str, prefix: str, suffix: str):
    """Feature: canonical-intent-engine, Property 3: Spelling variant round-trip lookup

    For any key in the spelling_variants map, normalizing text containing that
    key should produce text containing the corresponding canonical form.

    **Validates: Requirements 1.4**
    """
    canonical = SPELLING_VARIANTS[variant_key]

    # Build sanitized_text that embeds the variant key
    sanitized = f"{prefix} {variant_key} {suffix}".strip()
    assume(len(sanitized) > 0)

    record = InputRecord(
        sourceType="REAL",
        sourceId="test-id",
        rawText=sanitized,
        sanitizedText=sanitized,
    )
    state = PipelineState(record=record)
    result = normalize_text(state, TEST_CONFIG)

    assert canonical in result.normalized_text, (
        f"Expected canonical form {canonical!r} in normalized output "
        f"{result.normalized_text!r} (input contained variant {variant_key!r})"
    )
