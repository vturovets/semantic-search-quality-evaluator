"""Recommendation Engine — port of lib/quality-evaluation/recommendation-engine.ts.

Generates grounded, explainable recommendations from coverage, stability,
and paraphrase metrics.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from engine.priority_rules import PriorityInput, compute_priority
from engine.protection_rules import enforce_protection_rules


# ─── Config ─────────────────────────────────────────────────────────────────


@dataclass
class RecommendationEngineConfig:
    run_id: str
    materiality_threshold: float
    protected_case_rules: list[dict[str, Any]]
    observation_window: int = 30


# ─── Helpers ────────────────────────────────────────────────────────────────

_counter = 0


def _generate_id() -> str:
    global _counter
    _counter += 1
    return f"rec-{int(time.time() * 1000)}-{_counter}"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _make_audit(id_: str) -> dict[str, Any]:
    now = _now_iso()
    return {
        "id": id_,
        "createdAt": now,
        "createdBy": "recommendation-engine",
        "updatedAt": now,
        "version": 1,
    }


def _make_base_recommendation(
    run_id: str,
    type_: str,
    intent_id: str,
    intent_family: str,
    overrides: dict[str, Any],
) -> dict[str, Any]:
    """Build a base Recommendation shell with common defaults."""
    rec_id = _generate_id()
    base = {
        **_make_audit(rec_id),
        "recommendationId": rec_id,
        "runId": run_id,
        "type": type_,
        "affectedGoldenSet": "accuracy",
        "impactedIntentId": intent_id,
        "impactedIntentFamily": intent_family,
        "reason": "",
        "observedFrequency": 0,
        "observedSharePercent": 0,
        "currentGoldenRepresentation": 0,
        "identifiedGap": "",
        "proposedAction": "",
        "priority": "low",
        "status": "draft",
        "isProtected": False,
        "protectedClasses": [],
        "actionability": "insufficient-evidence",
        "supportingRecordIds": [],
        "supportingClusterIds": [],
    }
    base.update(overrides)
    return base


def _build_priority_input(
    metric: dict[str, Any],
    affects_governance: bool,
    affects_accuracy: bool,
    affects_consistency: bool,
) -> PriorityInput:
    """Build a PriorityInput from a coverage metric and recommendation context."""
    return PriorityInput(
        observed_share_percent=metric.get("realInputSharePercent", 0),
        actionability=metric.get("actionability", "insufficient-evidence"),
        is_protected=metric.get("isProtected", False),
        representation_delta=metric.get("representationDelta", 0),
        affects_governance=affects_governance,
        affects_accuracy=affects_accuracy,
        affects_consistency=affects_consistency,
    )


# ─── Main Engine ────────────────────────────────────────────────────────────


def generate_recommendations(
    coverage_metrics: list[dict[str, Any]],
    stability_metrics: list[dict[str, Any]],
    paraphrase_metrics: list[dict[str, Any]],
    config: RecommendationEngineConfig,
) -> list[dict[str, Any]]:
    """Generate grounded, explainable recommendations from coverage, stability,
    and paraphrase metrics.

    Covers all 8 recommendation types:
    1. add-new-intent — real-only intents that are action-ready or protected
    2. add-examples-for-intent — underrepresented intents
    3. add-paraphrase-variants — narrow paraphrase groups
    4. create-paraphrase-group — missing paraphrase groups
    5. add-unsupported-coverage — unsupported intents materially present
    6. add-policy-pii-coverage — policy/PII/non-English protected intents
    7. reduce-retire-obsolete — candidate-obsolete intents (NOT protected)
    8. no-update — matched intents with adequate coverage
    """
    recommendations: list[dict[str, Any]] = []
    run_id = config.run_id
    materiality_threshold = config.materiality_threshold
    protected_case_rules = config.protected_case_rules

    # Build a lookup of stability by intentId
    stability_by_intent: dict[str, dict[str, Any]] = {}
    for s in stability_metrics:
        stability_by_intent[s["intentId"]] = s

    # ── Process each coverage metric (intent-level recommendations) ──────

    for metric in coverage_metrics:
        stability = stability_by_intent.get(metric.get("intentId", ""))
        actionability = (
            stability["actionability"] if stability else metric.get("actionability", "insufficient-evidence")
        )
        is_protected = metric.get("isProtected", False)
        protected_classes = metric.get("protectedClasses", [])
        classification = metric.get("classification", "")
        intent_id = metric.get("intentId", "")
        intent_label = metric.get("intentLabel", "")
        intent_family = metric.get("intentFamily", "")
        real_input_count = metric.get("realInputCount", 0)
        real_input_share_percent = metric.get("realInputSharePercent", 0)
        golden_set_case_count = metric.get("goldenSetCaseCount", 0)
        golden_set_share_percent = metric.get("goldenSetSharePercent", 0)
        representation_delta = metric.get("representationDelta", 0)

        # ── 1. add-new-intent: real-only intents that are action-ready or protected
        if classification == "real-only":
            is_actionable = actionability in ("action-ready", "protected-override")
            is_monitor = actionability == "monitor"

            if is_actionable:
                recommendations.append(_make_base_recommendation(
                    run_id, "add-new-intent", intent_id, intent_family, {
                        "affectedGoldenSet": "accuracy",
                        "reason": (
                            f'Intent "{intent_label}" observed in real traffic '
                            f'({real_input_share_percent:.2f}% share) but absent from '
                            f'accuracy golden set. Statistically action-ready.'
                        ),
                        "observedFrequency": real_input_count,
                        "observedSharePercent": real_input_share_percent,
                        "currentGoldenRepresentation": golden_set_case_count,
                        "identifiedGap": "Intent missing from accuracy golden set",
                        "proposedAction": (
                            f'Add "{intent_label}" to accuracy golden set with '
                            f'representative test cases'
                        ),
                        "isProtected": is_protected,
                        "protectedClasses": protected_classes,
                        "actionability": actionability,
                        "priority": compute_priority(_build_priority_input(
                            metric, is_protected, True, False,
                        )),
                    },
                ))
            elif is_monitor:
                recommendations.append(_make_base_recommendation(
                    run_id, "add-new-intent", intent_id, intent_family, {
                        "affectedGoldenSet": "accuracy",
                        "reason": (
                            f'Intent "{intent_label}" observed in real traffic '
                            f'({real_input_share_percent:.2f}% share) but absent from '
                            f'accuracy golden set. Share not yet statistically stable — monitor.'
                        ),
                        "observedFrequency": real_input_count,
                        "observedSharePercent": real_input_share_percent,
                        "currentGoldenRepresentation": golden_set_case_count,
                        "identifiedGap": "Intent missing from accuracy golden set (monitor)",
                        "proposedAction": (
                            f'Monitor "{intent_label}" in next observation window '
                            f'before adding to golden set'
                        ),
                        "isProtected": is_protected,
                        "protectedClasses": protected_classes,
                        "actionability": "monitor",
                        "priority": compute_priority(_build_priority_input(
                            metric, False, True, False,
                        )),
                    },
                ))

        # ── 2. add-examples-for-intent: underrepresented intents
        if classification == "underrepresented":
            recommendations.append(_make_base_recommendation(
                run_id, "add-examples-for-intent", intent_id, intent_family, {
                    "affectedGoldenSet": "accuracy",
                    "reason": (
                        f'Intent "{intent_label}" is underrepresented in the golden set. '
                        f'Real share {real_input_share_percent:.2f}% vs golden share '
                        f'{golden_set_share_percent:.2f}% (delta {representation_delta:.2f}%).'
                    ),
                    "observedFrequency": real_input_count,
                    "observedSharePercent": real_input_share_percent,
                    "currentGoldenRepresentation": golden_set_case_count,
                    "identifiedGap": f"Representation delta: {representation_delta:.2f}%",
                    "proposedAction": (
                        f'Add more unique examples for "{intent_label}" to accuracy '
                        f'golden set to close the representation gap'
                    ),
                    "isProtected": is_protected,
                    "protectedClasses": protected_classes,
                    "actionability": actionability,
                    "priority": compute_priority(_build_priority_input(
                        metric, is_protected, True, False,
                    )),
                },
            ))

        # ── 5. add-unsupported-coverage: unsupported intents materially present
        if "unsupported-intent" in protected_classes and real_input_count > 0:
            share_above_threshold = real_input_share_percent >= materiality_threshold
            if share_above_threshold:
                recommendations.append(_make_base_recommendation(
                    run_id, "add-unsupported-coverage", intent_id, intent_family, {
                        "affectedGoldenSet": "accuracy",
                        "reason": (
                            f'Unsupported intent "{intent_label}" is materially present '
                            f'in real traffic ({real_input_share_percent:.2f}% share, '
                            f'threshold {materiality_threshold}%). Explicit coverage recommended.'
                        ),
                        "observedFrequency": real_input_count,
                        "observedSharePercent": real_input_share_percent,
                        "currentGoldenRepresentation": golden_set_case_count,
                        "identifiedGap": (
                            "Unsupported intent materially present without explicit "
                            "golden set coverage"
                        ),
                        "proposedAction": (
                            f'Add or retain explicit unsupported-intent coverage for '
                            f'"{intent_label}" in accuracy golden set'
                        ),
                        "isProtected": True,
                        "protectedClasses": protected_classes,
                        "actionability": "protected-override",
                        "priority": compute_priority(_build_priority_input(
                            metric, True, True, False,
                        )),
                    },
                ))

        # ── 6. add-policy-pii-coverage: policy/PII/non-English protected intents
        policy_pii_classes = ["policy-blocked", "pii-related", "non-english"]
        has_policy_pii_class = any(pc in policy_pii_classes for pc in protected_classes)
        if has_policy_pii_class and is_protected:
            if golden_set_case_count == 0 or classification == "real-only":
                recommendations.append(_make_base_recommendation(
                    run_id, "add-policy-pii-coverage", intent_id, intent_family, {
                        "affectedGoldenSet": "accuracy",
                        "reason": (
                            f'Protected intent "{intent_label}" (classes: '
                            f'{", ".join(protected_classes)}) requires explicit coverage '
                            f'for governance compliance.'
                        ),
                        "observedFrequency": real_input_count,
                        "observedSharePercent": real_input_share_percent,
                        "currentGoldenRepresentation": golden_set_case_count,
                        "identifiedGap": "Policy/PII/non-English intent lacks golden set coverage",
                        "proposedAction": (
                            f'Add or retain policy/PII/non-English coverage for '
                            f'"{intent_label}"'
                        ),
                        "isProtected": True,
                        "protectedClasses": protected_classes,
                        "actionability": "protected-override",
                        "priority": compute_priority(_build_priority_input(
                            metric, True, True, False,
                        )),
                    },
                ))

        # ── 7. reduce-retire-obsolete: candidate-obsolete intents
        if classification == "candidate-obsolete":
            single_window = config.observation_window <= 30
            recommendations.append(_make_base_recommendation(
                run_id, "reduce-retire-obsolete", intent_id, intent_family, {
                    "affectedGoldenSet": "accuracy",
                    "reason": (
                        f'Intent "{intent_label}" has zero real-input observations in this '
                        f'window but exists in golden set. Single observation window — '
                        f'review recommended, not auto-retirement.'
                    ) if single_window else (
                        f'Intent "{intent_label}" has zero real-input observations across '
                        f'extended window. Candidate for retirement review.'
                    ),
                    "observedFrequency": real_input_count,
                    "observedSharePercent": real_input_share_percent,
                    "currentGoldenRepresentation": golden_set_case_count,
                    "identifiedGap": "Golden set intent not observed in real traffic",
                    "proposedAction": (
                        f'Review "{intent_label}" in next observation window before retiring'
                    ) if single_window else (
                        f'Consider retiring "{intent_label}" from accuracy golden set '
                        f'after governance review'
                    ),
                    "isProtected": is_protected,
                    "protectedClasses": protected_classes,
                    "actionability": actionability,
                    "priority": compute_priority(_build_priority_input(
                        metric, is_protected, True, False,
                    )),
                },
            ))

        # ── 8. no-update: matched intents with adequate coverage
        if classification == "matched":
            recommendations.append(_make_base_recommendation(
                run_id, "no-update", intent_id, intent_family, {
                    "affectedGoldenSet": "accuracy",
                    "reason": (
                        f'Intent "{intent_label}" is adequately represented. '
                        f'Real share {real_input_share_percent:.2f}% ≈ golden share '
                        f'{golden_set_share_percent:.2f}%.'
                    ),
                    "observedFrequency": real_input_count,
                    "observedSharePercent": real_input_share_percent,
                    "currentGoldenRepresentation": golden_set_case_count,
                    "identifiedGap": "None — coverage is adequate",
                    "proposedAction": "No update recommended",
                    "isProtected": is_protected,
                    "protectedClasses": protected_classes,
                    "actionability": actionability,
                    "priority": compute_priority(_build_priority_input(
                        metric, False, False, False,
                    )),
                },
            ))

        # protected-retained: no-update with protected override
        if classification == "protected-retained":
            recommendations.append(_make_base_recommendation(
                run_id, "no-update", intent_id, intent_family, {
                    "affectedGoldenSet": "accuracy",
                    "reason": (
                        f'Protected intent "{intent_label}" retained regardless of '
                        f'traffic volume (classes: {", ".join(protected_classes)}).'
                    ),
                    "observedFrequency": real_input_count,
                    "observedSharePercent": real_input_share_percent,
                    "currentGoldenRepresentation": golden_set_case_count,
                    "identifiedGap": "None — protected case retained",
                    "proposedAction": "No update recommended — protected case",
                    "isProtected": True,
                    "protectedClasses": protected_classes,
                    "actionability": "protected-override",
                    "priority": compute_priority(_build_priority_input(
                        metric, True, False, False,
                    )),
                },
            ))

        # overrepresented: no-update with review note
        if classification == "overrepresented":
            recommendations.append(_make_base_recommendation(
                run_id, "no-update", intent_id, intent_family, {
                    "affectedGoldenSet": "accuracy",
                    "reason": (
                        f'Intent "{intent_label}" is overrepresented in golden set. '
                        f'Golden share {golden_set_share_percent:.2f}% vs real share '
                        f'{real_input_share_percent:.2f}%.'
                    ),
                    "observedFrequency": real_input_count,
                    "observedSharePercent": real_input_share_percent,
                    "currentGoldenRepresentation": golden_set_case_count,
                    "identifiedGap": f"Overrepresentation delta: {representation_delta:.2f}%",
                    "proposedAction": (
                        f'Review golden set allocation for "{intent_label}" — '
                        f'may have excess test cases'
                    ),
                    "isProtected": is_protected,
                    "protectedClasses": protected_classes,
                    "actionability": actionability,
                    "priority": compute_priority(_build_priority_input(
                        metric, False, True, False,
                    )),
                },
            ))

        # golden-only: reduce-retire-obsolete
        if classification == "golden-only":
            recommendations.append(_make_base_recommendation(
                run_id, "reduce-retire-obsolete", intent_id, intent_family, {
                    "affectedGoldenSet": "accuracy",
                    "reason": (
                        f'Intent "{intent_label}" exists only in golden set with '
                        f'no real-input observations.'
                    ),
                    "observedFrequency": 0,
                    "observedSharePercent": 0,
                    "currentGoldenRepresentation": golden_set_case_count,
                    "identifiedGap": "Golden-only intent — no real traffic observed",
                    "proposedAction": (
                        f'Review "{intent_label}" for potential retirement or '
                        f'reclassification'
                    ),
                    "isProtected": is_protected,
                    "protectedClasses": protected_classes,
                    "actionability": actionability,
                    "priority": compute_priority(_build_priority_input(
                        metric, is_protected, True, False,
                    )),
                },
            ))

    # ── Process paraphrase metrics (consistency-level recommendations) ────

    for pm in paraphrase_metrics:
        coverage_metric = next(
            (c for c in coverage_metrics if c.get("intentId") == pm.get("intentId")),
            None,
        )

        pm_intent_id = pm.get("intentId", "")
        pm_is_protected = pm.get("isProtected", False)
        pm_paraphrase_group_id = pm.get("paraphraseGroupId", "")
        pm_real_wording_variant_count = pm.get("realWordingVariantCount", 0)
        pm_golden_paraphrase_count = pm.get("goldenParaphraseCount", 0)
        pm_uncovered_variants = pm.get("uncoveredVariants", [])
        pm_has_instability_signal = pm.get("hasInstabilitySignal", False)
        pm_outcome_variability = pm.get("outcomeVariability", [])
        pm_classification = pm.get("classification", "")

        cm_share = coverage_metric.get("realInputSharePercent", 0) if coverage_metric else 0
        cm_actionability = coverage_metric.get("actionability", "insufficient-evidence") if coverage_metric else "insufficient-evidence"
        cm_delta = coverage_metric.get("representationDelta", 0) if coverage_metric else 0

        # ── 3. add-paraphrase-variants: narrow paraphrase groups
        if pm_classification == "narrow":
            priority_input = PriorityInput(
                observed_share_percent=cm_share,
                actionability=cm_actionability,
                is_protected=pm_is_protected,
                representation_delta=pm_real_wording_variant_count - pm_golden_paraphrase_count,
                affects_governance=pm_is_protected,
                affects_accuracy=False,
                affects_consistency=True,
            )

            recommendations.append(_make_base_recommendation(
                run_id, "add-paraphrase-variants", pm_intent_id, "", {
                    "affectedGoldenSet": "consistency",
                    "reason": (
                        f'Paraphrase group "{pm_paraphrase_group_id}" for intent '
                        f'"{pm_intent_id}" is narrow. {len(pm_uncovered_variants)} '
                        f'uncovered wording variant(s) found in real traffic.'
                    ),
                    "observedFrequency": pm_real_wording_variant_count,
                    "observedSharePercent": cm_share,
                    "currentGoldenRepresentation": pm_golden_paraphrase_count,
                    "identifiedGap": f"{len(pm_uncovered_variants)} uncovered wording variants",
                    "proposedAction": (
                        f'Add paraphrase variants to group "{pm_paraphrase_group_id}" '
                        f'to cover real-traffic wording breadth'
                    ),
                    "isProtected": pm_is_protected,
                    "protectedClasses": [],
                    "actionability": cm_actionability,
                    "priority": compute_priority(priority_input),
                },
            ))

        # ── 4. create-paraphrase-group: missing paraphrase groups
        if pm_classification == "missing":
            priority_input = PriorityInput(
                observed_share_percent=cm_share,
                actionability=cm_actionability,
                is_protected=pm_is_protected,
                representation_delta=0,
                affects_governance=pm_is_protected,
                affects_accuracy=False,
                affects_consistency=True,
            )

            recommendations.append(_make_base_recommendation(
                run_id, "create-paraphrase-group", pm_intent_id, "", {
                    "affectedGoldenSet": "consistency",
                    "reason": (
                        f'Paraphrase group "{pm_paraphrase_group_id}" for intent '
                        f'"{pm_intent_id}" has no matching real wording variants. '
                        f'Group may need creation or review.'
                    ),
                    "observedFrequency": pm_real_wording_variant_count,
                    "observedSharePercent": cm_share,
                    "currentGoldenRepresentation": pm_golden_paraphrase_count,
                    "identifiedGap": "No real wording variants found for paraphrase group",
                    "proposedAction": (
                        f'Create or review paraphrase group for intent "{pm_intent_id}"'
                    ),
                    "isProtected": pm_is_protected,
                    "protectedClasses": [],
                    "actionability": cm_actionability,
                    "priority": compute_priority(priority_input),
                },
            ))

        # ── Consistency-review: outcome variability detected
        if pm_has_instability_signal and len(pm_outcome_variability) > 1:
            priority_input = PriorityInput(
                observed_share_percent=cm_share,
                actionability=cm_actionability,
                is_protected=pm_is_protected,
                representation_delta=cm_delta,
                affects_governance=pm_is_protected,
                affects_accuracy=False,
                affects_consistency=True,
            )

            recommendations.append(_make_base_recommendation(
                run_id, "add-paraphrase-variants", pm_intent_id, "", {
                    "affectedGoldenSet": "consistency",
                    "reason": (
                        f'Intent "{pm_intent_id}" shows outcome variability across '
                        f'real traffic: [{", ".join(pm_outcome_variability)}]. '
                        f'Consistency set review recommended.'
                    ),
                    "observedFrequency": pm_real_wording_variant_count,
                    "observedSharePercent": cm_share,
                    "currentGoldenRepresentation": pm_golden_paraphrase_count,
                    "identifiedGap": (
                        f'Outcome variability detected: '
                        f'{", ".join(pm_outcome_variability)}'
                    ),
                    "proposedAction": (
                        f'Review and expand consistency set for intent "{pm_intent_id}" '
                        f'to cover outcome variability'
                    ),
                    "isProtected": pm_is_protected,
                    "protectedClasses": [],
                    "actionability": cm_actionability,
                    "priority": compute_priority(priority_input),
                },
            ))

    # ── Apply protection rules ──────────────────────────────────────────
    protected_recommendations = enforce_protection_rules(
        recommendations, protected_case_rules
    )

    return protected_recommendations
