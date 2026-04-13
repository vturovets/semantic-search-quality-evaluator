"""Consistency Metrics — port of lib/quality-evaluation/consistency-metrics.ts.

Higher-level paraphrase group analysis built on top of comparison.py.
"""

from __future__ import annotations

from typing import Any

from engine.comparison import ComparisonConfig, compare_wording_coverage


# ─── Instability Detection ──────────────────────────────────────────────────


def detect_instability(
    intent_id: str,
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    """Detect outcome variability for a given canonical intent.

    If the records for the same intentId have multiple distinct
    normalizedStatus values, that signals instability.
    """
    status_set: set[str] = set()
    for r in records:
        if r.get("normalizedIntent") == intent_id and r.get("normalizedStatus"):
            status_set.add(r["normalizedStatus"])

    statuses = list(status_set)
    return {
        "hasInstability": len(statuses) > 1,
        "statuses": statuses,
    }


# ─── analyzeParaphraseGroups ────────────────────────────────────────────────


def analyze_paraphrase_groups(
    normalized_real_inputs: list[dict[str, Any]],
    normalized_consistency_set: list[dict[str, Any]],
    config: ComparisonConfig,
) -> list[dict[str, Any]]:
    """Analyze paraphrase groups by:
    1. Calling compare_wording_coverage from comparison.py to get base metrics
    2. Enriching each metric with instability detection
    3. Returning ParaphraseCoverageMetric dicts
    """
    # 1. Get base metrics from comparison module
    base_metrics = compare_wording_coverage(
        normalized_real_inputs,
        normalized_consistency_set,
        config,
    )

    # 2. Enrich each metric with instability detection from real inputs
    result: list[dict[str, Any]] = []
    for metric in base_metrics:
        instability = detect_instability(
            metric["intentId"], normalized_real_inputs
        )
        enriched = {
            **metric,
            "hasInstabilitySignal": instability["hasInstability"],
            "outcomeVariability": instability["statuses"],
        }
        result.append(enriched)

    return result
