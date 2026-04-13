"""Unit tests for engine.intent_matching module.

Covers exact, synonym, and pattern matching functions plus the
MatchCandidate dataclass.
"""

from __future__ import annotations

from engine.intent_config import CatalogEntry
from engine.intent_matching import (
    MatchCandidate,
    find_exact_matches,
    find_pattern_matches,
    find_synonym_matches,
)


def _make_entry(**overrides) -> CatalogEntry:
    """Helper to build a CatalogEntry with sensible defaults."""
    defaults = {
        "intentId": "intent-1",
        "intentLabel": "Check Balance",
        "intentFamily": "billing",
        "intentClass": "SUPPORTED",
        "exactPhrases": [],
        "synonyms": [],
        "patterns": [],
        "priorityScore": 1.0,
        "protectedFlag": False,
    }
    defaults.update(overrides)
    return CatalogEntry(**defaults)


# ── MatchCandidate dataclass ────────────────────────────────────────────


class TestMatchCandidate:
    def test_fields(self):
        mc = MatchCandidate(
            intent_id="i1",
            intent_label="Label",
            match_type="exact",
            priority_score=0.9,
            matched_rule_id="exact:i1",
        )
        assert mc.intent_id == "i1"
        assert mc.match_type == "exact"
        assert mc.priority_score == 0.9
        assert mc.matched_rule_id == "exact:i1"


# ── find_exact_matches ──────────────────────────────────────────────────


class TestFindExactMatches:
    def test_match_found(self):
        entry = _make_entry(exactPhrases=["check balance", "view balance"])
        results = find_exact_matches("check balance", [entry])
        assert len(results) == 1
        assert results[0].match_type == "exact"
        assert results[0].matched_rule_id == "exact:intent-1"

    def test_no_match(self):
        entry = _make_entry(exactPhrases=["check balance"])
        results = find_exact_matches("pay bill", [entry])
        assert results == []

    def test_multiple_catalog_entries(self):
        e1 = _make_entry(intentId="i1", exactPhrases=["hello"])
        e2 = _make_entry(intentId="i2", exactPhrases=["hello"])
        results = find_exact_matches("hello", [e1, e2])
        assert len(results) == 2
        ids = {r.intent_id for r in results}
        assert ids == {"i1", "i2"}

    def test_empty_catalog(self):
        assert find_exact_matches("anything", []) == []

    def test_empty_text(self):
        entry = _make_entry(exactPhrases=["", "check balance"])
        results = find_exact_matches("", [entry])
        assert len(results) == 1


# ── find_synonym_matches ────────────────────────────────────────────────


class TestFindSynonymMatches:
    def test_match_found(self):
        entry = _make_entry(synonyms=["account balance", "balance inquiry"])
        results = find_synonym_matches("balance inquiry", [entry])
        assert len(results) == 1
        assert results[0].match_type == "synonym"
        assert results[0].matched_rule_id == "synonym:intent-1"

    def test_no_match(self):
        entry = _make_entry(synonyms=["account balance"])
        results = find_synonym_matches("pay bill", [entry])
        assert results == []

    def test_empty_catalog(self):
        assert find_synonym_matches("anything", []) == []


# ── find_pattern_matches ────────────────────────────────────────────────


class TestFindPatternMatches:
    def test_match_found(self):
        entry = _make_entry(patterns=[r"check.*balance"])
        results = find_pattern_matches("check my balance", [entry], token_count=3)
        assert len(results) == 1
        assert results[0].match_type == "pattern"
        assert results[0].matched_rule_id == "pattern:intent-1:0"

    def test_short_input_returns_empty(self):
        entry = _make_entry(patterns=[r".*"])
        assert find_pattern_matches("hi", [entry], token_count=1) == []
        assert find_pattern_matches("hi there", [entry], token_count=2) == []

    def test_three_tokens_allowed(self):
        entry = _make_entry(patterns=[r".*"])
        results = find_pattern_matches("one two three", [entry], token_count=3)
        assert len(results) == 1

    def test_invalid_regex_skipped(self):
        entry = _make_entry(patterns=[r"[invalid", r"valid.*pattern"])
        results = find_pattern_matches("valid test pattern", [entry], token_count=3)
        assert len(results) == 1
        assert results[0].matched_rule_id == "pattern:intent-1:1"

    def test_no_match(self):
        entry = _make_entry(patterns=[r"^xyz$"])
        results = find_pattern_matches("abc", [entry], token_count=3)
        assert results == []

    def test_multiple_patterns_same_entry(self):
        entry = _make_entry(patterns=[r"foo", r"bar"])
        results = find_pattern_matches("foobar", [entry], token_count=3)
        assert len(results) == 2
        rule_ids = {r.matched_rule_id for r in results}
        assert rule_ids == {"pattern:intent-1:0", "pattern:intent-1:1"}

    def test_empty_catalog(self):
        assert find_pattern_matches("anything", [], token_count=5) == []

    def test_priority_score_propagated(self):
        entry = _make_entry(patterns=[r"test"], priorityScore=0.75)
        results = find_pattern_matches("test input here", [entry], token_count=3)
        assert results[0].priority_score == 0.75
