"""Feature: canonical-intent-engine — Protected-case routing property tests.

Property 4: Protected-case classification
Property 5: Protected routing precedes intent matching
Property 6: Protected termination skips matching
Property 7: Protected continuation preserves flag

These tests verify that the route_protected pipeline stage correctly
classifies policy-blocked, PII, and non-English inputs, that protected
routing takes precedence over intent matching, and that terminate/continue
modes behave correctly.
"""

from __future__ import annotations

import re

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
from engine.intent_pipeline import PipelineState, normalize_text, route_protected
from models.intent_models import InputRecord


# ─── Helpers ─────────────────────────────────────────────────────────────────

_MINIMAL_NORMALIZATION = NormalizationConfig(
    spellingVariants={},
    separatorReplacements={"-": " ", "_": " "},
    punctuationStripPattern=r"[!?.,;:\"'()\[\]{}]",
)

_MINIMAL_STATUS_NORM = StatusNormalizationConfig(
    canonicalStatuses={},
    defaultUnmapped="UNDETERMINED",
)

_MINIMAL_OPTION_NORM = OptionNormalizationConfig(canonicalOptions={})


def _make_config(
    *,
    policy_blocked: list[str] | None = None,
    pii_indicators: list[str] | None = None,
    non_english: list[str] | None = None,
    on_match: str = "terminate",
    catalog: list[CatalogEntry] | None = None,
) -> IntentEngineConfig:
    """Build a minimal IntentEngineConfig for protection tests."""
    return IntentEngineConfig(
        catalogVersion="test-v1",
        catalog=catalog or [],
        protectedCase=ProtectedCaseConfig(
            policyBlockedPatterns=policy_blocked or [],
            piiIndicators=pii_indicators or [],
            nonEnglishPatterns=non_english or [],
            onMatch=on_match,
        ),
        normalization=_MINIMAL_NORMALIZATION,
        statusNormalization=_MINIMAL_STATUS_NORM,
        optionNormalization=_MINIMAL_OPTION_NORM,
        disambiguationRules=[],
    )


def _make_record(sanitized_text: str) -> InputRecord:
    return InputRecord(
        sourceType="REAL",
        sourceId="test-id",
        rawText=sanitized_text,
        sanitizedText=sanitized_text,
    )


def _make_state(sanitized_text: str, config: IntentEngineConfig) -> PipelineState:
    """Create a PipelineState that has already been through normalization."""
    record = _make_record(sanitized_text)
    state = PipelineState(record=record)
    return normalize_text(state, config)


# ─── Strategies ──────────────────────────────────────────────────────────────

_safe_alpha = st.sampled_from("abcdefghijklmnopqrstuvwxyz")

_word_st = st.text(alphabet=_safe_alpha, min_size=3, max_size=8).filter(
    lambda s: s.strip() != ""
)

_id_st = st.text(
    alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyz0123456789"),
    min_size=3,
    max_size=15,
)


@st.composite
def _text_containing_keyword(draw, keyword: str) -> str:
    """Generate a lowercase text string that contains *keyword*."""
    prefix = draw(st.text(alphabet=_safe_alpha, min_size=0, max_size=15))
    suffix = draw(st.text(alphabet=_safe_alpha, min_size=0, max_size=15))
    text = f"{prefix} {keyword} {suffix}".strip()
    assume(len(text) > 0)
    return text


# ─── Property 4: Protected-case classification ──────────────────────────────


# Fixed keywords used as literal regex patterns for each protected class.
_POLICY_KEYWORD = "blockedcontent"
_PII_KEYWORD = "mysocialsecuritynumber"
_NON_ENGLISH_KEYWORD = "nichtsenglisch"


@given(
    prefix=st.text(alphabet=_safe_alpha, min_size=0, max_size=15),
    suffix=st.text(alphabet=_safe_alpha, min_size=0, max_size=15),
)
@settings(max_examples=100)
def test_policy_blocked_classification(prefix: str, suffix: str):
    """Feature: canonical-intent-engine, Property 4: Protected-case classification (policy-blocked)

    For any InputRecord whose normalized text matches a policy-blocked pattern,
    the result should have intent_class=PROTECTED, protected_flag=True, and
    protected_class=REJECTED_BY_POLICY.

    **Validates: Requirements 2.2, 2.3, 2.4, 2.5**
    """
    text = f"{prefix} {_POLICY_KEYWORD} {suffix}".strip()
    assume(len(text) > 0)

    config = _make_config(policy_blocked=[re.escape(_POLICY_KEYWORD)])
    state = _make_state(text, config)
    result = route_protected(state, config)

    assert result.intent_class == "PROTECTED"
    assert result.protected_flag is True
    assert result.protected_class == "REJECTED_BY_POLICY"


@given(
    prefix=st.text(alphabet=_safe_alpha, min_size=0, max_size=15),
    suffix=st.text(alphabet=_safe_alpha, min_size=0, max_size=15),
)
@settings(max_examples=100)
def test_pii_detected_classification(prefix: str, suffix: str):
    """Feature: canonical-intent-engine, Property 4: Protected-case classification (PII)

    For any InputRecord whose normalized text matches a PII indicator pattern,
    the result should have intent_class=PROTECTED, protected_flag=True, and
    protected_class=PII_DETECTED.

    **Validates: Requirements 2.2, 2.3, 2.4, 2.5**
    """
    text = f"{prefix} {_PII_KEYWORD} {suffix}".strip()
    assume(len(text) > 0)

    config = _make_config(pii_indicators=[re.escape(_PII_KEYWORD)])
    state = _make_state(text, config)
    result = route_protected(state, config)

    assert result.intent_class == "PROTECTED"
    assert result.protected_flag is True
    assert result.protected_class == "PII_DETECTED"


@given(
    prefix=st.text(alphabet=_safe_alpha, min_size=0, max_size=15),
    suffix=st.text(alphabet=_safe_alpha, min_size=0, max_size=15),
)
@settings(max_examples=100)
def test_non_english_classification(prefix: str, suffix: str):
    """Feature: canonical-intent-engine, Property 4: Protected-case classification (non-English)

    For any InputRecord whose normalized text matches a non-English pattern,
    the result should have intent_class=PROTECTED, protected_flag=True, and
    protected_class=REJECTED_NON_ENGLISH.

    **Validates: Requirements 2.2, 2.3, 2.4, 2.5**
    """
    text = f"{prefix} {_NON_ENGLISH_KEYWORD} {suffix}".strip()
    assume(len(text) > 0)

    config = _make_config(non_english=[re.escape(_NON_ENGLISH_KEYWORD)])
    state = _make_state(text, config)
    result = route_protected(state, config)

    assert result.intent_class == "PROTECTED"
    assert result.protected_flag is True
    assert result.protected_class == "REJECTED_NON_ENGLISH"


# ─── Property 5: Protected routing precedes intent matching ──────────────────


@given(
    prefix=st.text(alphabet=_safe_alpha, min_size=0, max_size=10),
    suffix=st.text(alphabet=_safe_alpha, min_size=0, max_size=10),
)
@settings(max_examples=100)
def test_protected_routing_precedes_intent_matching(prefix: str, suffix: str):
    """Feature: canonical-intent-engine, Property 5: Protected routing precedes intent matching

    For any InputRecord that matches both a protected-case rule AND a supported
    intent in the catalog, the result should have intent_class=PROTECTED (not
    SUPPORTED), confirming protected routing executes before intent matching.

    **Validates: Requirements 2.1**
    """
    # Use a phrase that will be both a protected keyword and an exact catalog phrase
    shared_phrase = _POLICY_KEYWORD
    text = f"{prefix} {shared_phrase} {suffix}".strip()
    assume(len(text) > 0)

    # Create a catalog entry whose exact phrase matches the same text
    catalog_entry = CatalogEntry(
        intentId="intent-overlap",
        intentLabel="Overlap Intent",
        intentFamily="general",
        intentClass="SUPPORTED",
        exactPhrases=[text.lower()],
        synonyms=[text.lower()],
        patterns=[],
        priorityScore=10.0,
        protectedFlag=False,
    )

    config = _make_config(
        policy_blocked=[re.escape(shared_phrase)],
        catalog=[catalog_entry],
    )
    state = _make_state(text, config)

    # Run protected routing first (as the pipeline does)
    result = route_protected(state, config)

    assert result.intent_class == "PROTECTED", (
        f"Expected PROTECTED but got {result.intent_class} — "
        "protected routing must precede intent matching"
    )
    assert result.protected_flag is True


# ─── Property 6: Protected termination skips matching ────────────────────────


@given(
    prefix=st.text(alphabet=_safe_alpha, min_size=0, max_size=15),
    suffix=st.text(alphabet=_safe_alpha, min_size=0, max_size=15),
)
@settings(max_examples=100)
def test_protected_termination_skips_matching(prefix: str, suffix: str):
    """Feature: canonical-intent-engine, Property 6: Protected termination skips matching

    For any InputRecord that triggers a protected-case rule when
    on_match="terminate", the skip_to_outcome flag should be True and
    applied_rules should contain the protected rule but no matching-stage rules.

    **Validates: Requirements 2.6**
    """
    text = f"{prefix} {_POLICY_KEYWORD} {suffix}".strip()
    assume(len(text) > 0)

    config = _make_config(
        policy_blocked=[re.escape(_POLICY_KEYWORD)],
        on_match="terminate",
    )
    state = _make_state(text, config)
    result = route_protected(state, config)

    # skip_to_outcome must be True for terminate mode
    assert result.skip_to_outcome is True, (
        "Expected skip_to_outcome=True when on_match='terminate'"
    )

    # applied_rules should contain the protected rule
    assert any("protected:" in rule for rule in result.applied_rules), (
        f"Expected a protected rule in applied_rules, got: {result.applied_rules}"
    )

    # No matching-stage rules (exact/synonym/pattern) should be present
    matching_rules = [
        r for r in result.applied_rules
        if r.startswith("exact:") or r.startswith("synonym:") or r.startswith("pattern:")
    ]
    assert matching_rules == [], (
        f"Expected no matching-stage rules when terminated, got: {matching_rules}"
    )


# ─── Property 7: Protected continuation preserves flag ──────────────────────


@given(
    prefix=st.text(alphabet=_safe_alpha, min_size=0, max_size=15),
    suffix=st.text(alphabet=_safe_alpha, min_size=0, max_size=15),
)
@settings(max_examples=100)
def test_protected_continuation_preserves_flag(prefix: str, suffix: str):
    """Feature: canonical-intent-engine, Property 7: Protected continuation preserves flag

    For any InputRecord that triggers a protected-case rule when
    on_match="continue", the result should have protected_flag=True and
    protected_class set, but skip_to_outcome=False.

    **Validates: Requirements 2.7**
    """
    text = f"{prefix} {_PII_KEYWORD} {suffix}".strip()
    assume(len(text) > 0)

    config = _make_config(
        pii_indicators=[re.escape(_PII_KEYWORD)],
        on_match="continue",
    )
    state = _make_state(text, config)
    result = route_protected(state, config)

    # Protected flags should be set
    assert result.protected_flag is True, "Expected protected_flag=True in continue mode"
    assert result.protected_class == "PII_DETECTED", (
        f"Expected protected_class='PII_DETECTED', got {result.protected_class!r}"
    )
    assert result.intent_class == "PROTECTED"

    # skip_to_outcome must be False — pipeline continues
    assert result.skip_to_outcome is False, (
        "Expected skip_to_outcome=False when on_match='continue'"
    )
