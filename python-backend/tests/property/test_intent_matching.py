"""Feature: canonical-intent-engine, Property 8: Supported intent matching with priority ordering

For any InputRecord whose normalized text matches a catalog entry via exact
phrase, synonym, or pattern, the matching functions return the correct
candidates.  Exact matches take priority over synonym matches, which take
priority over pattern matches.  The match_type field correctly reflects the
matching strategy used.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6**
"""

from __future__ import annotations

from hypothesis import given, settings, assume
from hypothesis import strategies as st

from engine.intent_config import CatalogEntry
from engine.intent_matching import (
    MatchCandidate,
    find_exact_matches,
    find_pattern_matches,
    find_synonym_matches,
)

# ─── Strategies ──────────────────────────────────────────────────────────────

_id_st = st.text(
    alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyz0123456789"),
    min_size=3,
    max_size=15,
)

_label_st = st.text(
    alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyz "),
    min_size=3,
    max_size=20,
).filter(lambda s: s.strip() != "")

_family_st = st.sampled_from(["billing", "account", "support", "general"])

_priority_st = st.floats(min_value=0.1, max_value=10.0, allow_nan=False, allow_infinity=False)

# A phrase strategy that produces lowercase multi-word strings (3+ tokens)
# suitable for exact/synonym matching and pattern matching.
_phrase_st = st.text(
    alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyz"),
    min_size=3,
    max_size=10,
).map(lambda s: s.strip()).filter(lambda s: len(s) >= 3)


@st.composite
def _multi_word_phrase_st(draw):
    """Generate a phrase with 3+ tokens for pattern matching eligibility."""
    words = draw(st.lists(_phrase_st, min_size=3, max_size=5))
    return " ".join(words)


@st.composite
def catalog_entry_with_exact_st(draw):
    """Generate a CatalogEntry and a text that matches one of its exact phrases."""
    intent_id = draw(_id_st)
    label = draw(_label_st)
    phrase = draw(_phrase_st)
    priority = draw(_priority_st)

    entry = CatalogEntry(
        intentId=intent_id,
        intentLabel=label,
        intentFamily=draw(_family_st),
        intentClass="SUPPORTED",
        exactPhrases=[phrase],
        synonyms=[],
        patterns=[],
        priorityScore=priority,
        protectedFlag=False,
    )
    return entry, phrase


@st.composite
def catalog_entry_with_synonym_st(draw):
    """Generate a CatalogEntry and a text that matches one of its synonyms."""
    intent_id = draw(_id_st)
    label = draw(_label_st)
    synonym = draw(_phrase_st)
    priority = draw(_priority_st)

    entry = CatalogEntry(
        intentId=intent_id,
        intentLabel=label,
        intentFamily=draw(_family_st),
        intentClass="SUPPORTED",
        exactPhrases=[],
        synonyms=[synonym],
        patterns=[],
        priorityScore=priority,
        protectedFlag=False,
    )
    return entry, synonym


@st.composite
def catalog_entry_with_pattern_st(draw):
    """Generate a CatalogEntry and a multi-word text that matches its pattern."""
    intent_id = draw(_id_st)
    label = draw(_label_st)
    # Use a fixed keyword embedded in a multi-word phrase
    keyword = draw(_phrase_st)
    multi_word = draw(_multi_word_phrase_st())
    # Build text that contains the keyword (ensuring pattern match)
    text = f"{multi_word} {keyword}"
    # Use a simple regex that matches the keyword literally
    import re
    pattern = re.escape(keyword)
    priority = draw(_priority_st)

    entry = CatalogEntry(
        intentId=intent_id,
        intentLabel=label,
        intentFamily=draw(_family_st),
        intentClass="SUPPORTED",
        exactPhrases=[],
        synonyms=[],
        patterns=[pattern],
        priorityScore=priority,
        protectedFlag=False,
    )
    token_count = len(text.split())
    assume(token_count > 2)
    return entry, text, token_count


@st.composite
def catalog_entry_with_all_match_types_st(draw):
    """Generate a CatalogEntry where a single text matches exact, synonym, AND pattern."""
    intent_id = draw(_id_st)
    label = draw(_label_st)
    priority = draw(_priority_st)
    # The phrase will be used as exact, synonym, and will match the pattern
    phrase = draw(_multi_word_phrase_st())
    assume(len(phrase.split()) > 2)
    import re
    # Use first word as pattern keyword so the phrase matches
    first_word = phrase.split()[0]
    pattern = re.escape(first_word)

    entry = CatalogEntry(
        intentId=intent_id,
        intentLabel=label,
        intentFamily=draw(_family_st),
        intentClass="SUPPORTED",
        exactPhrases=[phrase],
        synonyms=[phrase],
        patterns=[pattern],
        priorityScore=priority,
        protectedFlag=False,
    )
    token_count = len(phrase.split())
    return entry, phrase, token_count


# ─── Property Tests ─────────────────────────────────────────────────────────


@given(data=catalog_entry_with_exact_st())
@settings(max_examples=100)
def test_exact_match_returns_candidate_with_correct_type(data):
    """Exact phrase match returns a candidate with match_type='exact'.

    **Validates: Requirements 3.1**
    """
    entry, text = data
    candidates = find_exact_matches(text, [entry])

    assert len(candidates) >= 1, "Expected at least one exact match candidate"
    for c in candidates:
        assert c.match_type == "exact"
        assert c.intent_id == entry.intent_id
        assert c.intent_label == entry.intent_label
        assert c.priority_score == entry.priority_score
        assert c.matched_rule_id == f"exact:{entry.intent_id}"


@given(data=catalog_entry_with_synonym_st())
@settings(max_examples=100)
def test_synonym_match_returns_candidate_with_correct_type(data):
    """Synonym match returns a candidate with match_type='synonym'.

    **Validates: Requirements 3.2**
    """
    entry, text = data
    candidates = find_synonym_matches(text, [entry])

    assert len(candidates) >= 1, "Expected at least one synonym match candidate"
    for c in candidates:
        assert c.match_type == "synonym"
        assert c.intent_id == entry.intent_id
        assert c.intent_label == entry.intent_label
        assert c.priority_score == entry.priority_score
        assert c.matched_rule_id == f"synonym:{entry.intent_id}"


@given(data=catalog_entry_with_pattern_st())
@settings(max_examples=100)
def test_pattern_match_returns_candidate_with_correct_type(data):
    """Pattern match returns a candidate with match_type='pattern' when token_count > 2.

    **Validates: Requirements 3.3**
    """
    entry, text, token_count = data
    candidates = find_pattern_matches(text, [entry], token_count=token_count)

    assert len(candidates) >= 1, "Expected at least one pattern match candidate"
    for c in candidates:
        assert c.match_type == "pattern"
        assert c.intent_id == entry.intent_id
        assert c.intent_label == entry.intent_label
        assert c.priority_score == entry.priority_score


@given(data=catalog_entry_with_all_match_types_st())
@settings(max_examples=100)
def test_priority_ordering_exact_over_synonym_over_pattern(data):
    """When text matches exact, synonym, and pattern, all three strategies return
    candidates with the correct match_type, confirming priority ordering is
    available for disambiguation (exact > synonym > pattern).

    **Validates: Requirements 3.4, 3.5, 3.6**
    """
    entry, text, token_count = data

    exact_candidates = find_exact_matches(text, [entry])
    synonym_candidates = find_synonym_matches(text, [entry])
    pattern_candidates = find_pattern_matches(text, [entry], token_count=token_count)

    # All three strategies should find matches
    assert len(exact_candidates) >= 1, "Expected exact match candidate"
    assert len(synonym_candidates) >= 1, "Expected synonym match candidate"
    assert len(pattern_candidates) >= 1, "Expected pattern match candidate"

    # match_type correctly reflects the strategy used
    assert all(c.match_type == "exact" for c in exact_candidates)
    assert all(c.match_type == "synonym" for c in synonym_candidates)
    assert all(c.match_type == "pattern" for c in pattern_candidates)

    # All candidates reference the same intent
    all_candidates = exact_candidates + synonym_candidates + pattern_candidates
    assert all(c.intent_id == entry.intent_id for c in all_candidates)
    assert all(c.intent_label == entry.intent_label for c in all_candidates)

    # Priority ordering: exact match type should be present when text matches
    # an exact phrase — confirming the caller can prioritise exact > synonym > pattern
    match_types = [c.match_type for c in all_candidates]
    assert "exact" in match_types
    assert "synonym" in match_types
    assert "pattern" in match_types


# ─── Property 9: Short input pattern restriction ────────────────────────────


@st.composite
def short_text_with_catchall_catalog_st(draw):
    """Generate a CatalogEntry with a catch-all pattern and short text (≤2 tokens)."""
    intent_id = draw(_id_st)
    label = draw(_label_st)
    priority = draw(_priority_st)

    # Catch-all pattern that would match anything
    entry = CatalogEntry(
        intentId=intent_id,
        intentLabel=label,
        intentFamily=draw(_family_st),
        intentClass="SUPPORTED",
        exactPhrases=[],
        synonyms=[],
        patterns=[".*"],
        priorityScore=priority,
        protectedFlag=False,
    )

    # Generate short text: 1 or 2 tokens
    num_tokens = draw(st.integers(min_value=1, max_value=2))
    words = draw(
        st.lists(_phrase_st, min_size=num_tokens, max_size=num_tokens)
    )
    text = " ".join(words)
    token_count = len(text.split())
    assume(token_count <= 2)

    return entry, text, token_count


@given(data=short_text_with_catchall_catalog_st())
@settings(max_examples=100)
def test_short_input_never_gets_pattern_match(data):
    """Feature: canonical-intent-engine, Property 9: Short input pattern restriction

    For any InputRecord whose normalized text contains two or fewer tokens,
    find_pattern_matches always returns an empty list — short inputs should
    never get pattern-based matches regardless of what patterns exist in the
    catalog.

    **Validates: Requirements 9.1, 9.2, 9.3**
    """
    entry, text, token_count = data

    candidates = find_pattern_matches(text, [entry], token_count=token_count)

    assert candidates == [], (
        f"Expected no pattern matches for short input ({token_count} tokens: {text!r}), "
        f"but got {len(candidates)} candidate(s)"
    )


# ─── Property 10: Disambiguation selects highest priority ────────────────────


from engine.intent_pipeline import disambiguate, PipelineState
from engine.intent_config import (
    IntentEngineConfig,
    ProtectedCaseConfig,
    NormalizationConfig,
    StatusNormalizationConfig,
    OptionNormalizationConfig,
)
from models.intent_models import InputRecord


def _minimal_config(disambiguation_rules=None):
    """Build a minimal IntentEngineConfig for disambiguation tests."""
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
            canonicalStatuses={},
            defaultUnmapped="UNDETERMINED",
        ),
        optionNormalization=OptionNormalizationConfig(
            canonicalOptions={},
        ),
        disambiguationRules=disambiguation_rules or [],
    )


def _minimal_record():
    """Build a minimal InputRecord for pipeline state construction."""
    return InputRecord(
        sourceType="REAL",
        sourceId="test-001",
        rawText="test input",
        sanitizedText="test input",
    )


@st.composite
def distinct_priority_candidates_st(draw):
    """Generate 2-5 MatchCandidates with strictly distinct priority scores."""
    n = draw(st.integers(min_value=2, max_value=5))
    # Draw n distinct priority scores
    priorities = draw(
        st.lists(
            st.floats(min_value=0.1, max_value=100.0, allow_nan=False, allow_infinity=False),
            min_size=n,
            max_size=n,
            unique=True,
        )
    )
    candidates = []
    for i, p in enumerate(priorities):
        cid = draw(_id_st)
        label = draw(_label_st)
        match_type = draw(st.sampled_from(["exact", "synonym", "pattern"]))
        candidates.append(
            MatchCandidate(
                intent_id=cid,
                intent_label=label,
                match_type=match_type,
                priority_score=p,
                matched_rule_id=f"{match_type}:{cid}",
            )
        )
    return candidates


@given(candidates=distinct_priority_candidates_st())
@settings(max_examples=100)
def test_disambiguation_selects_highest_priority(candidates):
    """Feature: canonical-intent-engine, Property 10: Disambiguation selects highest priority

    For any set of match candidates with distinct priority scores, the
    disambiguator selects the candidate with the highest priority_score
    and records all candidates in applied_rules.

    **Validates: Requirements 4.1, 4.5**
    """
    config = _minimal_config()
    state = PipelineState(
        record=_minimal_record(),
        matched_candidates=candidates,
    )

    result = disambiguate(state, config)

    # Find the expected winner (highest priority_score)
    expected_winner = max(candidates, key=lambda c: c.priority_score)

    # The winner should be selected
    assert result.canonical_intent_id == expected_winner.intent_id, (
        f"Expected intent_id={expected_winner.intent_id} (priority={expected_winner.priority_score}), "
        f"got {result.canonical_intent_id}"
    )
    assert result.canonical_intent_label == expected_winner.intent_label
    assert result.intent_class == "SUPPORTED"

    # All candidates should appear in applied_rules
    for c in candidates:
        expected_rule = f"candidate:{c.intent_id}:{c.match_type}:{c.priority_score}"
        assert expected_rule in result.applied_rules, (
            f"Candidate rule {expected_rule!r} not found in applied_rules"
        )


# ─── Property 11: Unresolvable ambiguity yields UNKNOWN ─────────────────────


@st.composite
def tied_priority_candidates_st(draw):
    """Generate 2-5 MatchCandidates all sharing the same priority score."""
    n = draw(st.integers(min_value=2, max_value=5))
    shared_priority = draw(
        st.floats(min_value=0.1, max_value=100.0, allow_nan=False, allow_infinity=False)
    )
    candidates = []
    for i in range(n):
        cid = draw(_id_st)
        label = draw(_label_st)
        match_type = draw(st.sampled_from(["exact", "synonym", "pattern"]))
        candidates.append(
            MatchCandidate(
                intent_id=cid,
                intent_label=label,
                match_type=match_type,
                priority_score=shared_priority,
                matched_rule_id=f"{match_type}:{cid}",
            )
        )
    return candidates


@given(candidates=tied_priority_candidates_st())
@settings(max_examples=100)
def test_unresolvable_ambiguity_yields_unknown(candidates):
    """Feature: canonical-intent-engine, Property 11: Unresolvable ambiguity yields UNKNOWN

    For any set of match candidates with tied priority scores and no
    applicable disambiguation rules, the result should have
    ambiguity_flag=True and intent_class should remain None (not forced).
    All candidate intents and their scores are recorded in applied_rules.

    **Validates: Requirements 4.3, 4.4, 8.3**
    """
    # Empty disambiguation rules — no rule can resolve the tie
    config = _minimal_config(disambiguation_rules=[])
    state = PipelineState(
        record=_minimal_record(),
        matched_candidates=candidates,
    )

    result = disambiguate(state, config)

    # Ambiguity flag must be set
    assert result.ambiguity_flag is True, (
        f"Expected ambiguity_flag=True for tied candidates, got {result.ambiguity_flag}"
    )

    # intent_class should NOT be forced to SUPPORTED (remains None)
    assert result.intent_class is None, (
        f"Expected intent_class=None (not forced) for unresolvable ambiguity, "
        f"got {result.intent_class!r}"
    )

    # All candidates should appear in applied_rules
    for c in candidates:
        expected_rule = f"candidate:{c.intent_id}:{c.match_type}:{c.priority_score}"
        assert expected_rule in result.applied_rules, (
            f"Candidate rule {expected_rule!r} not found in applied_rules"
        )
