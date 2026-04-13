"""Statistical Evaluation — port of lib/quality-evaluation/statistical-evaluation.ts.

Wilson score confidence interval computation and actionability classification.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Literal


# ─── Z-Score Lookup ─────────────────────────────────────────────────────────

Z_SCORE_TABLE: dict[float, float] = {
    0.80: 1.2816,
    0.85: 1.4395,
    0.90: 1.6449,
    0.95: 1.96,
    0.99: 2.5758,
}


def z_score_for_confidence(confidence_level: float) -> float:
    """Look up the z-score for a given confidence level.
    Falls back to 1.96 (95%) if the level is not in the table.
    """
    return Z_SCORE_TABLE.get(confidence_level, 1.96)


# ─── Wilson Score Interval ──────────────────────────────────────────────────


def wilson_score_interval(
    successes: int,
    total: int,
    confidence_level: float = 0.95,
) -> dict[str, Any]:
    """Compute the Wilson score confidence interval for a binomial proportion.

    Formula:
      p̂ = successes / n
      z = z-score for confidence level
      center = (p̂ + z²/(2n)) / (1 + z²/n)
      margin = z / (1 + z²/n) * sqrt(p̂(1-p̂)/n + z²/(4n²))
      lower = center - margin
      upper = center + margin
    """
    if total == 0:
        return {
            "lower": 0,
            "upper": 0,
            "observedShare": 0,
            "sampleSize": 0,
            "confidenceLevel": confidence_level,
            "method": "wilson-score",
        }

    z = z_score_for_confidence(confidence_level)
    n = total
    p_hat = successes / n
    z_squared = z * z

    denominator = 1 + z_squared / n
    center = (p_hat + z_squared / (2 * n)) / denominator
    margin = (z / denominator) * math.sqrt(
        (p_hat * (1 - p_hat)) / n + z_squared / (4 * n * n)
    )

    return {
        "lower": max(0, center - margin),
        "upper": min(1, center + margin),
        "observedShare": p_hat,
        "sampleSize": n,
        "confidenceLevel": confidence_level,
        "method": "wilson-score",
    }


# ─── Actionability Classification ───────────────────────────────────────────


def classify_actionability(
    ci: dict[str, Any],
    materiality_threshold: float,
    min_sample_size: int,
    is_protected: bool,
) -> str:
    """Classify an intent's actionability based on its confidence interval,
    materiality threshold, sample size, and protected status.

    Rules:
     - protected → 'protected-override'
     - sampleSize < minSampleSize → 'insufficient-evidence'
     - lower CI bound >= materialityThreshold → 'action-ready'
     - observedShare >= threshold but lower < threshold → 'monitor'
     - else → 'insufficient-evidence'
    """
    if is_protected:
        return "protected-override"
    if ci["sampleSize"] < min_sample_size:
        return "insufficient-evidence"
    if ci["lower"] >= materiality_threshold:
        return "action-ready"
    if ci["observedShare"] >= materiality_threshold and ci["lower"] < materiality_threshold:
        return "monitor"
    return "insufficient-evidence"


# ─── Intent Stability Evaluation ────────────────────────────────────────────


@dataclass
class IntentObservation:
    intent_id: str
    observed_count: int


@dataclass
class StabilityEvaluationConfig:
    run_id: str = ""
    confidence_level: float = 0.95
    materiality_threshold: float = 0.01
    min_sample_size: int = 1000
    protected_intents: dict[str, bool] | None = None


def evaluate_intent_stability(
    intents: list[IntentObservation],
    total_sample: int,
    config: StabilityEvaluationConfig | None = None,
) -> list[dict[str, Any]]:
    """Evaluate statistical stability for every intent in the provided array.
    Returns one IntentShareStabilityMetric per intent.
    """
    if config is None:
        config = StabilityEvaluationConfig()

    protected_intents = config.protected_intents or {}
    now = datetime.now(timezone.utc).isoformat()

    results: list[dict[str, Any]] = []

    for intent in intents:
        ci = wilson_score_interval(
            intent.observed_count, total_sample, config.confidence_level
        )
        is_protected = protected_intents.get(intent.intent_id, False)
        actionability = classify_actionability(
            ci, config.materiality_threshold, config.min_sample_size, is_protected
        )
        meets_min = total_sample >= config.min_sample_size

        if actionability == "action-ready":
            rationale = (
                f"Lower CI bound ({ci['lower']:.4f}) >= materiality threshold "
                f"({config.materiality_threshold}); sample size {total_sample} "
                f"meets minimum {config.min_sample_size}."
            )
        elif actionability == "monitor":
            rationale = (
                f"Observed share ({ci['observedShare']:.4f}) >= threshold "
                f"({config.materiality_threshold}) but lower CI bound "
                f"({ci['lower']:.4f}) < threshold; recommend monitoring."
            )
        elif actionability == "protected-override":
            rationale = (
                "Intent is protected; actionability overridden regardless of "
                "statistical volume."
            )
        else:  # insufficient-evidence
            if meets_min:
                rationale = (
                    f"Observed share ({ci['observedShare']:.4f}) below materiality "
                    f"threshold ({config.materiality_threshold})."
                )
            else:
                rationale = (
                    f"Sample size {total_sample} below minimum "
                    f"{config.min_sample_size}; insufficient evidence."
                )

        results.append({
            "id": f"stability-{intent.intent_id}",
            "createdAt": now,
            "createdBy": "system",
            "updatedAt": now,
            "version": 1,
            "runId": config.run_id,
            "intentId": intent.intent_id,
            "observedCount": intent.observed_count,
            "totalSampleSize": total_sample,
            "observedShare": ci["observedShare"],
            "confidenceInterval": ci,
            "materialityThreshold": config.materiality_threshold,
            "actionability": actionability,
            "meetsMinSampleSize": meets_min,
            "rationale": rationale,
        })

    return results
