"""Pipeline stages for the Canonical Intent Determination Engine.

Each stage is a pure function: ``(PipelineState, IntentEngineConfig) -> PipelineState``.
Stages use ``dataclasses.replace()`` to return new state objects, never mutating
the incoming state or the original ``InputRecord``.

Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field, replace

from engine.intent_config import IntentEngineConfig
from engine.intent_matching import (
    MatchCandidate,
    find_exact_matches,
    find_pattern_matches,
    find_synonym_matches,
)
from models.enums import IntentClass
from models.intent_models import InputRecord


@dataclass
class PipelineState:
    """Carries all intermediate values through the pipeline stages."""

    record: InputRecord
    normalized_text: str = ""
    intent_class: IntentClass | None = None
    canonical_intent_id: str | None = None
    canonical_intent_label: str | None = None
    protected_class: str | None = None
    protected_flag: bool = False
    matched_candidates: list[MatchCandidate] = field(default_factory=list)
    decision_method: str | None = None
    applied_rules: list[str] = field(default_factory=list)
    ambiguity_flag: bool = False
    normalized_status: str | None = None
    normalized_option_signature: str | None = None
    comparison_anchor: str | None = None
    error_message: str | None = None
    skip_to_outcome: bool = False


# ── Stage 1: Text Normalization ─────────────────────────────────────────────


def normalize_text(state: PipelineState, config: IntentEngineConfig) -> PipelineState:
    """Normalize the input text for downstream matching.

    Steps (in order):
    1. Lowercase                          (Req 1.1)
    2. Strip / normalize punctuation      (Req 1.2)
    3. Replace separators                 (Req 1.3)
    4. Apply spelling variants            (Req 1.4)
    5. Collapse extra whitespace

    Returns a *new* ``PipelineState`` — the original ``record`` is never
    mutated (Req 1.5).
    """
    text = state.record.sanitized_text

    # 1. Lowercase (Req 1.1)
    text = text.lower()

    # 2. Strip/normalize punctuation (Req 1.2)
    text = re.sub(config.normalization.punctuation_strip_pattern, " ", text)

    # 3. Apply spelling variants (Req 1.4) — before separator replacement so
    #    that compound variants containing separators (e.g. "wi-fi" → "wifi")
    #    are matched before the separator is stripped.
    for variant, canonical in config.normalization.spelling_variants.items():
        text = text.replace(variant, canonical)

    # 4. Replace separators (Req 1.3)
    for old, new in config.normalization.separator_replacements.items():
        text = text.replace(old, new)

    # 5. Collapse extra whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Return new state without mutating the original (Req 1.5)
    return replace(state, normalized_text=text)


# ── Stage 2: Protected-Case Routing ─────────────────────────────────────────


def route_protected(state: PipelineState, config: IntentEngineConfig) -> PipelineState:
    """Route protected-case inputs before intent matching.

    Checks ``normalized_text`` against the configured protected-case patterns
    in priority order:

    1. ``policy_blocked_patterns`` → ``REJECTED_BY_POLICY``
    2. ``pii_indicators``         → ``PII_DETECTED``
    3. ``non_english_patterns``   → ``REJECTED_NON_ENGLISH``

    On the first match the state is updated with ``intent_class = PROTECTED``,
    the appropriate ``protected_class``, and ``protected_flag = True``.  If the
    configuration specifies ``on_match = "terminate"`` the ``skip_to_outcome``
    flag is set so that downstream matching stages are bypassed.

    Invalid regex patterns are silently skipped so that a single bad rule does
    not break the entire pipeline.

    Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7
    """
    pc = config.protected_case
    text = state.normalized_text

    # Each tuple: (list of patterns, protected_class label)
    checks: list[tuple[list[str], str]] = [
        (pc.policy_blocked_patterns, "REJECTED_BY_POLICY"),
        (pc.pii_indicators, "PII_DETECTED"),
        (pc.non_english_patterns, "REJECTED_NON_ENGLISH"),
    ]

    for patterns, protected_class_value in checks:
        for pattern in patterns:
            try:
                if re.search(pattern, text):
                    return replace(
                        state,
                        intent_class="PROTECTED",
                        protected_class=protected_class_value,
                        protected_flag=True,
                        applied_rules=[
                            *state.applied_rules,
                            f"protected:{protected_class_value}:{pattern}",
                        ],
                        skip_to_outcome=pc.on_match == "terminate",
                    )
            except re.error:
                # Gracefully skip invalid regex patterns
                continue

    return state


# ── Stage 3: Supported Intent Matching ───────────────────────────────────────


def match_supported(state: PipelineState, config: IntentEngineConfig) -> PipelineState:
    """Match normalized text against the intent catalog.

    Skips matching entirely when ``skip_to_outcome`` is already set (e.g. by
    a protected-case termination in stage 2).

    Calls the three matching strategies in priority order (Req 3.4):
    exact → synonym → pattern.  Pattern matching is automatically suppressed
    for short inputs (≤ 2 tokens) inside ``find_pattern_matches``
    (Requirements 9.1, 9.2).

    Requirements: 3.1, 3.2, 3.3, 3.4, 9.1, 9.2
    """
    if state.skip_to_outcome:
        return state

    token_count = len(state.normalized_text.split())

    exact = find_exact_matches(state.normalized_text, config.catalog)
    synonym = find_synonym_matches(state.normalized_text, config.catalog)
    pattern = find_pattern_matches(state.normalized_text, config.catalog, token_count)

    matched_candidates = [*exact, *synonym, *pattern]

    return replace(state, matched_candidates=matched_candidates)


# ── Stage 4: Disambiguation ──────────────────────────────────────────────────


def disambiguate(state: PipelineState, config: IntentEngineConfig) -> PipelineState:
    """Resolve matched candidates to a single canonical intent or flag ambiguity.

    1. If ``skip_to_outcome`` is already set, return state unchanged.
    2. If there are no ``matched_candidates``, return state unchanged (later
       stages handle the no-match case).
    3. Record every candidate in ``applied_rules``.
    4. Single candidate → assign directly.
    5. Multiple candidates → pick highest ``priority_score``; if tied, attempt
       rule-based resolution via ``config.disambiguation_rules``; if still
       unresolvable, set ``ambiguity_flag = True`` without forcing an intent.

    Requirements: 4.1, 4.2, 4.3, 4.4, 4.5
    """
    if state.skip_to_outcome:
        return state

    candidates = state.matched_candidates
    if not candidates:
        return state

    # Record all candidates in applied_rules (Req 4.5)
    new_rules = [
        *state.applied_rules,
        *(
            f"candidate:{c.intent_id}:{c.match_type}:{c.priority_score}"
            for c in candidates
        ),
    ]

    # ── Single candidate ────────────────────────────────────────────────
    if len(candidates) == 1:
        winner = candidates[0]
        return replace(
            state,
            canonical_intent_id=winner.intent_id,
            canonical_intent_label=winner.intent_label,
            intent_class="SUPPORTED",
            decision_method=winner.match_type,
            applied_rules=new_rules,
        )

    # ── Multiple candidates ─────────────────────────────────────────────
    sorted_candidates = sorted(candidates, key=lambda c: c.priority_score, reverse=True)
    top = sorted_candidates[0]
    second = sorted_candidates[1]

    # Strictly higher priority → select top candidate (Req 4.1)
    if top.priority_score > second.priority_score:
        return replace(
            state,
            canonical_intent_id=top.intent_id,
            canonical_intent_label=top.intent_label,
            intent_class="SUPPORTED",
            decision_method=top.match_type,
            applied_rules=new_rules,
        )

    # Tied priorities → attempt rule-based resolution (Req 4.2)
    for rule in config.disambiguation_rules:
        if rule.condition == "highest_priority":
            winner = sorted_candidates[0]
            return replace(
                state,
                canonical_intent_id=winner.intent_id,
                canonical_intent_label=winner.intent_label,
                intent_class="SUPPORTED",
                decision_method=winner.match_type,
                applied_rules=new_rules,
            )

    # Unresolvable → flag ambiguity, do NOT force assignment (Req 4.3, 4.4)
    return replace(
        state,
        ambiguity_flag=True,
        applied_rules=new_rules,
    )


# ── Stage 5: Unsupported Intent Detection ────────────────────────────────────


def detect_unsupported(state: PipelineState, config: IntentEngineConfig) -> PipelineState:
    """Detect unsupported intents when no supported match was assigned.

    Runs only when the input has not already been classified as SUPPORTED,
    PROTECTED, or UNKNOWN, and is not flagged as ambiguous (which
    ``handle_unknown`` will resolve).

    If the normalized text matches an UNSUPPORTED catalog entry (via its
    exact_phrases, synonyms, or patterns), the specific unsupported label is
    assigned.  Otherwise a generic ``GENERIC_UNSUPPORTED`` label is used and
    the normalized text is recorded in ``applied_rules`` for traceability.

    Requirements: 7.1, 7.2, 7.3, 7.4
    """
    # 1. Early exits
    if state.skip_to_outcome:
        return state

    if state.intent_class in ("SUPPORTED", "PROTECTED", "UNKNOWN"):
        return state

    if state.ambiguity_flag:
        return state

    # 2. Search UNSUPPORTED catalog entries for a match
    for entry in config.catalog:
        if entry.intent_class != "UNSUPPORTED":
            continue

        matched = False

        # Check exact phrases
        if state.normalized_text in entry.exact_phrases:
            matched = True

        # Check synonyms
        if not matched and state.normalized_text in entry.synonyms:
            matched = True

        # Check patterns
        if not matched:
            for pattern in entry.patterns:
                try:
                    if re.search(pattern, state.normalized_text):
                        matched = True
                        break
                except re.error:
                    continue

        if matched:
            return replace(
                state,
                intent_class="UNSUPPORTED",
                canonical_intent_id=entry.intent_id,
                canonical_intent_label=entry.intent_label,
                normalized_status="NO_VALID_MAPPING",
                decision_method="unsupported",
                applied_rules=[*state.applied_rules, f"unsupported:{entry.intent_id}"],
            )

    # 3. No matching unsupported entry — assign generic unsupported
    return replace(
        state,
        intent_class="UNSUPPORTED",
        canonical_intent_label="GENERIC_UNSUPPORTED",
        normalized_status="NO_VALID_MAPPING",
        decision_method="unsupported",
        applied_rules=[*state.applied_rules, state.normalized_text],
    )


# ── Stage 6: Unknown Handling ────────────────────────────────────────────────


def handle_unknown(state: PipelineState, config: IntentEngineConfig) -> PipelineState:
    """Classify unresolved inputs as UNKNOWN.

    Runs when no earlier stage has assigned an ``intent_class`` — either
    because no match was found at all, or because the disambiguator flagged
    ambiguity without forcing an assignment.

    On activation the stage sets ``intent_class = "UNKNOWN"``,
    ``normalized_status = "UNDETERMINED"``, and ``decision_method = "unknown"``.
    The original ``sanitized_text`` is already carried on the ``record`` and
    will be propagated to the final result by downstream stages.

    Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 9.3
    """
    # 1. Protected-case termination — nothing to do
    if state.skip_to_outcome:
        return state

    # 2. Already classified — nothing to do
    if state.intent_class in ("SUPPORTED", "UNSUPPORTED", "PROTECTED"):
        return state

    # 3. Determine the reason tag for applied_rules
    reason = "unknown:ambiguous" if state.ambiguity_flag else "unknown:no_match"

    return replace(
        state,
        intent_class="UNKNOWN",
        normalized_status="UNDETERMINED",
        decision_method="unknown",
        applied_rules=[*state.applied_rules, reason],
    )


# ── Stage 7: Outcome Normalization ───────────────────────────────────────────


def normalize_outcome(state: PipelineState, config: IntentEngineConfig) -> PipelineState:
    """Normalize status and option values to canonical forms.

    1. Status normalization:
       - UNSUPPORTED → ``NO_VALID_MAPPING``
       - UNKNOWN → ``UNDETERMINED``
       - Otherwise: look up ``record.expected_status`` in
         ``config.status_normalization.canonical_statuses``; use canonical
         value if found, else ``config.status_normalization.default_unmapped``.
       - If a previous stage already set ``normalized_status`` (e.g.
         ``detect_unsupported`` or ``handle_unknown``), keep it for
         UNSUPPORTED / UNKNOWN classes; for SUPPORTED, derive from record.

    2. Option normalization:
       - Each value in ``record.expected_options`` is looked up in
         ``config.option_normalization.canonical_options``; unmatched values
         are lowercased and trimmed.
       - Normalized options are joined with ``,`` to form the option
         signature.  No options → empty string.

    3. Catalog defaults for SUPPORTED intents:
       - If the record has no ``expected_status`` and a catalog entry was
         matched, use the entry's ``default_status``.
       - If the record has no ``expected_options`` and a catalog entry was
         matched, use the entry's ``default_option_signature``.

    Requirements: 5.1, 5.2, 5.3, 5.4
    """
    normalized_status = state.normalized_status
    normalized_option_signature = state.normalized_option_signature

    # ── 1. Status normalization ─────────────────────────────────────────
    if state.intent_class == "UNSUPPORTED":
        normalized_status = "NO_VALID_MAPPING"
    elif state.intent_class == "UNKNOWN":
        normalized_status = "UNDETERMINED"
    else:
        # For SUPPORTED / PROTECTED / other: derive from record or catalog
        raw_status = state.record.expected_status

        # 3a. Catalog default for SUPPORTED with no expected_status
        if raw_status is None and state.intent_class == "SUPPORTED" and state.canonical_intent_id:
            matched_entry = _find_catalog_entry(state.canonical_intent_id, config)
            if matched_entry and matched_entry.default_status:
                raw_status = matched_entry.default_status

        if raw_status is not None:
            canonical = config.status_normalization.canonical_statuses.get(raw_status)
            normalized_status = canonical if canonical is not None else config.status_normalization.default_unmapped
        elif normalized_status is None:
            # No status from record or previous stage
            normalized_status = config.status_normalization.default_unmapped

    # ── 2. Option normalization ─────────────────────────────────────────
    expected_options = state.record.expected_options

    # 3b. Catalog default for SUPPORTED with no expected_options
    if expected_options is None and state.intent_class == "SUPPORTED" and state.canonical_intent_id:
        matched_entry = _find_catalog_entry(state.canonical_intent_id, config)
        if matched_entry and matched_entry.default_option_signature:
            normalized_option_signature = matched_entry.default_option_signature
        else:
            normalized_option_signature = ""
    elif expected_options is not None:
        normalized_opts: list[str] = []
        for opt in expected_options:
            canonical_opt = config.option_normalization.canonical_options.get(opt)
            if canonical_opt is not None:
                normalized_opts.append(canonical_opt)
            else:
                normalized_opts.append(opt.strip().lower())
        normalized_option_signature = ",".join(normalized_opts)
    else:
        normalized_option_signature = normalized_option_signature if normalized_option_signature is not None else ""

    return replace(
        state,
        normalized_status=normalized_status,
        normalized_option_signature=normalized_option_signature,
    )


def _find_catalog_entry(intent_id: str, config: IntentEngineConfig):
    """Look up a catalog entry by intent_id.  Returns ``None`` if not found."""
    for entry in config.catalog:
        if entry.intent_id == intent_id:
            return entry
    return None


# ── Stage 8: Comparison Anchor Generation ────────────────────────────────────


def build_anchor(state: PipelineState, config: IntentEngineConfig) -> PipelineState:
    """Build a pipe-delimited comparison anchor string based on intent_class.

    Format per intent class:
    - SUPPORTED:   ``SUPPORTED | <label> | <status> | <options>``
    - UNSUPPORTED: ``UNSUPPORTED | NO_VALID_MAPPING | <label>``
    - UNKNOWN:     ``UNKNOWN | UNDETERMINED | <sanitized_text>``
    - PROTECTED:   ``PROTECTED | <protected_class> | <sanitized_text>``

    If ``intent_class`` is ``None`` (defensive), falls back to the UNKNOWN
    format.

    Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
    """
    sep = " | "
    intent_class = state.intent_class

    if intent_class == "SUPPORTED":
        anchor = sep.join([
            "SUPPORTED",
            state.canonical_intent_label or "",
            state.normalized_status or "",
            state.normalized_option_signature or "",
        ])
    elif intent_class == "UNSUPPORTED":
        anchor = sep.join([
            "UNSUPPORTED",
            "NO_VALID_MAPPING",
            state.canonical_intent_label or "",
        ])
    elif intent_class == "PROTECTED":
        anchor = sep.join([
            "PROTECTED",
            state.protected_class or "",
            state.record.sanitized_text,
        ])
    else:
        # UNKNOWN or None (defensive fallback)
        anchor = sep.join([
            "UNKNOWN",
            "UNDETERMINED",
            state.record.sanitized_text,
        ])

    return replace(state, comparison_anchor=anchor)
