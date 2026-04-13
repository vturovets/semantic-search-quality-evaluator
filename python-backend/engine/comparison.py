"""Comparison Engine — port of lib/quality-evaluation/comparison.ts.

Three-way comparison across real-input, accuracy, and consistency datasets.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal


# ─── Config ─────────────────────────────────────────────────────────────────


@dataclass
class ComparisonConfig:
    run_id: str
    materiality_threshold: float
    min_sample_size: int
    confidence_level: float
    protected_intent_ids: set[str]


# ─── Helpers ────────────────────────────────────────────────────────────────

_counter = 0


def _generate_id() -> str:
    global _counter
    _counter += 1
    return f"cmp-{int(time.time() * 1000)}-{_counter}"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _make_audit(id_: str) -> dict[str, Any]:
    now = _now_iso()
    return {
        "id": id_,
        "createdAt": now,
        "createdBy": "comparison-engine",
        "updatedAt": now,
        "version": 1,
    }


def group_by_intent(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group an array of NormalizedRecords by normalizedIntent."""
    result: dict[str, list[dict[str, Any]]] = {}
    for r in records:
        key = r.get("normalizedIntent", "")
        if key not in result:
            result[key] = []
        result[key].append(r)
    return result


def collect_protected_classes(records: list[dict[str, Any]]) -> list[str]:
    """Collect all unique protected classes from a set of records."""
    classes: set[str] = set()
    for r in records:
        original_values = r.get("originalValues", {})
        raw = original_values.get("protectedClassHint") or original_values.get("protectedClass")
        if raw:
            classes.add(raw)
    return list(classes)


def placeholder_ci(
    observed_share: float,
    sample_size: int,
    confidence_level: float,
) -> dict[str, Any]:
    """Placeholder confidence interval — filled by statistical_evaluation later."""
    return {
        "lower": 0,
        "upper": 0,
        "observedShare": observed_share,
        "sampleSize": sample_size,
        "confidenceLevel": confidence_level,
        "method": "wilson-score",
    }


# ─── Intent Classification ──────────────────────────────────────────────────


def classify_intent(
    real_count: int,
    golden_count: int,
    real_share: float,
    golden_share: float,
    is_protected: bool,
    materiality_threshold: float,
) -> str:
    """Classify a single canonical intent into one of 7 groups.

    Mirrors the TypeScript classifyIntent function exactly.
    """
    if is_protected and golden_count > 0 and real_count == 0:
        return "protected-retained"
    if real_count > 0 and golden_count == 0:
        return "real-only"
    if real_count == 0 and golden_count > 0:
        return "protected-retained" if is_protected else "candidate-obsolete"
    if real_count > 0 and golden_count > 0:
        delta = real_share - golden_share
        if abs(delta) < materiality_threshold:
            return "matched"
        if delta > 0:
            return "underrepresented"
        return "overrepresented"
    return "matched"  # fallback — both zero


# ─── compareIntentCoverage ──────────────────────────────────────────────────


def compare_intent_coverage(
    normalized_real_inputs: list[dict[str, Any]],
    normalized_accuracy_set: list[dict[str, Any]],
    config: ComparisonConfig,
) -> list[dict[str, Any]]:
    """Compare normalised real-input records against normalised accuracy golden-set
    records and produce an IntentCoverageMetric for every canonical intent found
    in the union of both datasets.
    """
    # 1. Group by normalizedIntent
    real_by_intent = group_by_intent(normalized_real_inputs)
    golden_by_intent = group_by_intent(normalized_accuracy_set)

    # 2. Build union of all intents
    all_intents = set(real_by_intent.keys()) | set(golden_by_intent.keys())

    total_real = len(normalized_real_inputs)
    total_golden = len(normalized_accuracy_set)

    metrics: list[dict[str, Any]] = []

    # 3. For each intent, compute counts, shares, delta, classification
    for intent_id in all_intents:
        real_records = real_by_intent.get(intent_id, [])
        golden_records = golden_by_intent.get(intent_id, [])

        real_count = len(real_records)
        golden_count = len(golden_records)

        real_share = real_count / total_real if total_real > 0 else 0
        golden_share = golden_count / total_golden if total_golden > 0 else 0
        delta = real_share - golden_share

        is_protected = intent_id in config.protected_intent_ids
        protected_classes = collect_protected_classes(real_records + golden_records)

        classification = classify_intent(
            real_count,
            golden_count,
            real_share,
            golden_share,
            is_protected,
            config.materiality_threshold,
        )

        is_recommendation_candidate = classification != "matched"

        id_ = _generate_id()
        metric = {
            **_make_audit(id_),
            "runId": config.run_id,
            "intentId": intent_id,
            "intentLabel": intent_id,
            "intentFamily": "",
            "classification": classification,
            "realInputCount": real_count,
            "realInputSharePercent": real_share * 100,
            "goldenSetCaseCount": golden_count,
            "goldenSetSharePercent": golden_share * 100,
            "representationDelta": delta * 100,
            "isProtected": is_protected,
            "protectedClasses": protected_classes,
            "isRecommendationCandidate": is_recommendation_candidate,
            "confidenceInterval": placeholder_ci(real_share, total_real, config.confidence_level),
            "actionability": "insufficient-evidence",
        }
        metrics.append(metric)

    return metrics


# ─── compareWordingCoverage ─────────────────────────────────────────────────


def classify_paraphrase_group(
    golden_count: int,
    real_variant_count: int,
    uncovered_count: int,
    is_protected: bool,
) -> str:
    """Classify a paraphrase group based on golden vs real wording coverage.

    - protected-retained: intent is protected regardless of coverage
    - missing: no real wording variants found at all
    - narrow: golden set has fewer variants than real traffic (uncovered > 0)
    - adequately-represented: golden set covers real wording breadth
    """
    if is_protected:
        return "protected-retained"
    if real_variant_count == 0:
        return "missing"
    if uncovered_count > 0:
        return "narrow"
    return "adequately-represented"


def compare_wording_coverage(
    normalized_real_inputs: list[dict[str, Any]],
    normalized_consistency_set: list[dict[str, Any]],
    config: ComparisonConfig,
) -> list[dict[str, Any]]:
    """Compare normalised real-input records against normalised consistency
    golden-set records and produce a ParaphraseCoverageMetric for every
    paraphrase group.
    """
    # 1. Group consistency records by sourceTestCaseId (paraphrase group)
    group_map: dict[str, list[dict[str, Any]]] = {}
    for r in normalized_consistency_set:
        original_values = r.get("originalValues", {})
        group_id = original_values.get("sourceTestCaseId") or r.get("originalSourceId", "")
        if group_id not in group_map:
            group_map[group_id] = []
        group_map[group_id].append(r)

    # Index real inputs by normalizedIntent for fast lookup
    real_by_intent = group_by_intent(normalized_real_inputs)

    metrics: list[dict[str, Any]] = []

    # 2. For each paraphrase group
    for group_id, group_records in group_map.items():
        # All records in a paraphrase group share the same canonical intent
        intent_id = group_records[0].get("normalizedIntent", "")
        is_protected = intent_id in config.protected_intent_ids
        protected_classes = collect_protected_classes(group_records)

        golden_paraphrase_count = len(group_records)

        # 3. Find matching real-input records by normalizedIntent
        matching_real = real_by_intent.get(intent_id, [])

        # Collect unique real wording variants
        real_wordings: set[str] = set()
        for r in matching_real:
            ov = r.get("originalValues", {})
            text = ov.get("sanitizedText") or ov.get("freeTextInput") or ""
            if text:
                real_wordings.add(text)

        # Collect golden wording variants
        golden_wordings: set[str] = set()
        for r in group_records:
            ov = r.get("originalValues", {})
            text = ov.get("freeTextInput") or ov.get("sanitizedText") or ""
            if text:
                golden_wordings.add(text)

        # Uncovered variants: real wordings not present in golden set
        uncovered_variants = [w for w in real_wordings if w not in golden_wordings]

        real_wording_variant_count = len(real_wordings)

        # Detect instability
        status_set: set[str] = set()
        for r in matching_real:
            ns = r.get("normalizedStatus")
            if ns:
                status_set.add(ns)
        has_instability_signal = len(status_set) > 1
        outcome_variability = list(status_set)

        # 4. Classify
        classification = classify_paraphrase_group(
            golden_paraphrase_count,
            real_wording_variant_count,
            len(uncovered_variants),
            is_protected,
        )

        id_ = _generate_id()
        metric = {
            **_make_audit(id_),
            "runId": config.run_id,
            "intentId": intent_id,
            "paraphraseGroupId": group_id,
            "classification": classification,
            "goldenParaphraseCount": golden_paraphrase_count,
            "realWordingVariantCount": real_wording_variant_count,
            "uncoveredVariants": uncovered_variants,
            "isProtected": is_protected,
            "hasInstabilitySignal": has_instability_signal,
            "outcomeVariability": outcome_variability,
        }
        metrics.append(metric)

    return metrics
