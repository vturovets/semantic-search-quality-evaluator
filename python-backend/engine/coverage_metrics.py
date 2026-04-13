"""Coverage Metrics — port of lib/quality-evaluation/coverage-metrics.ts.

Intent classification into 7 groups and aggregate coverage summary.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.comparison import classify_intent


# ─── CoverageMetricsSummary ─────────────────────────────────────────────────


@dataclass
class CoverageMetricsSummary:
    matched: int = 0
    real_only: int = 0
    golden_only: int = 0
    underrepresented: int = 0
    overrepresented: int = 0
    candidate_obsolete: int = 0
    protected_retained: int = 0
    total: int = 0


# ─── Classification key map ─────────────────────────────────────────────────

CLASSIFICATION_KEY_MAP: dict[str, str] = {
    "matched": "matched",
    "real-only": "real_only",
    "golden-only": "golden_only",
    "underrepresented": "underrepresented",
    "overrepresented": "overrepresented",
    "candidate-obsolete": "candidate_obsolete",
    "protected-retained": "protected_retained",
}


# ─── classifyIntents ────────────────────────────────────────────────────────


def classify_intents(
    coverage_data: list[dict[str, Any]],
    materiality_threshold: float,
    protected_intent_ids: set[str],
) -> list[dict[str, Any]]:
    """Classify (or re-classify) each intent in the coverage data using the
    deterministic classification function.

    Returns a new list with updated classification fields.
    """
    result: list[dict[str, Any]] = []
    for metric in coverage_data:
        real_share = metric["realInputSharePercent"] / 100
        golden_share = metric["goldenSetSharePercent"] / 100
        is_protected = (
            metric.get("isProtected", False)
            or metric.get("intentId", "") in protected_intent_ids
        )

        classification = classify_intent(
            metric["realInputCount"],
            metric["goldenSetCaseCount"],
            real_share,
            golden_share,
            is_protected,
            materiality_threshold,
        )

        updated = {
            **metric,
            "classification": classification,
            "isProtected": is_protected,
            "isRecommendationCandidate": classification != "matched",
        }
        result.append(updated)

    return result


# ─── computeCoverageMetrics ─────────────────────────────────────────────────


def compute_coverage_metrics(
    classified_intents: list[dict[str, Any]],
) -> CoverageMetricsSummary:
    """Aggregate classified intents into a summary object with counts per
    classification group and a total.
    """
    summary = CoverageMetricsSummary()

    for intent in classified_intents:
        classification = intent.get("classification", "matched")
        attr_name = CLASSIFICATION_KEY_MAP.get(classification, "matched")
        current = getattr(summary, attr_name, 0)
        setattr(summary, attr_name, current + 1)
        summary.total += 1

    return summary
