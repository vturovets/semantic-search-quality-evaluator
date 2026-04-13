"""Intent matching logic for the Canonical Intent Determination Engine.

Encapsulates exact, synonym, and pattern matching strategies against the
intent catalog.  Each function returns a list of ``MatchCandidate`` objects
that the pipeline's disambiguation stage will resolve.

Requirements: 3.1, 3.2, 3.3, 3.4, 9.1, 9.2
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from engine.intent_config import CatalogEntry


@dataclass
class MatchCandidate:
    """A single candidate produced by one of the matching strategies."""

    intent_id: str
    intent_label: str
    match_type: Literal["exact", "synonym", "pattern"]
    priority_score: float
    matched_rule_id: str


def find_exact_matches(
    text: str,
    catalog: list[CatalogEntry],
) -> list[MatchCandidate]:
    """Return candidates whose ``exact_phrases`` contain *text*.

    Comparison is case-sensitive — callers are expected to pass already-
    normalised text and the catalog phrases should be stored in the same
    normalised form.
    """
    candidates: list[MatchCandidate] = []
    for entry in catalog:
        if text in entry.exact_phrases:
            candidates.append(
                MatchCandidate(
                    intent_id=entry.intent_id,
                    intent_label=entry.intent_label,
                    match_type="exact",
                    priority_score=entry.priority_score,
                    matched_rule_id=f"exact:{entry.intent_id}",
                )
            )
    return candidates


def find_synonym_matches(
    text: str,
    catalog: list[CatalogEntry],
) -> list[MatchCandidate]:
    """Return candidates whose ``synonyms`` list contains *text*."""
    candidates: list[MatchCandidate] = []
    for entry in catalog:
        if text in entry.synonyms:
            candidates.append(
                MatchCandidate(
                    intent_id=entry.intent_id,
                    intent_label=entry.intent_label,
                    match_type="synonym",
                    priority_score=entry.priority_score,
                    matched_rule_id=f"synonym:{entry.intent_id}",
                )
            )
    return candidates


def find_pattern_matches(
    text: str,
    catalog: list[CatalogEntry],
    token_count: int,
) -> list[MatchCandidate]:
    """Return candidates whose regex ``patterns`` match *text*.

    Returns an empty list when *token_count* ≤ 2 to prevent semantic
    over-generalisation on short inputs (Requirements 9.1, 9.2).

    Invalid regex patterns are silently skipped so that a single bad
    pattern does not break the entire matching pass.
    """
    if token_count <= 2:
        return []

    candidates: list[MatchCandidate] = []
    for entry in catalog:
        for idx, pattern in enumerate(entry.patterns):
            try:
                if re.search(pattern, text):
                    candidates.append(
                        MatchCandidate(
                            intent_id=entry.intent_id,
                            intent_label=entry.intent_label,
                            match_type="pattern",
                            priority_score=entry.priority_score,
                            matched_rule_id=f"pattern:{entry.intent_id}:{idx}",
                        )
                    )
            except re.error:
                # Gracefully skip invalid regex patterns.
                continue
    return candidates
