"""Protection Rules — port of lib/quality-evaluation/protection-rules.ts.

Protected-case enforcement for recommendations (FR-10, Requirement 11).
"""

from __future__ import annotations

from typing import Any


# ─── Protected Classes ──────────────────────────────────────────────────────

PROTECTED_CLASSES: list[str] = [
    "policy-blocked",
    "pii-related",
    "non-english",
    "unsupported-intent",
    "rule-behavior-sensitive",
]


# ─── isProtected ────────────────────────────────────────────────────────────


def is_protected(
    record: dict[str, Any],
    protected_case_rules: list[dict[str, Any]],
) -> bool:
    """Check whether a record/intent is protected according to the enabled rules.

    A record is considered protected when it carries a `protectedClass`,
    `protectedClassHint`, or `protectedClasses` value that matches at least one
    enabled entry in `protectedCaseRules`.
    """
    enabled_classes: set[str] = set()
    for rule in protected_case_rules:
        if rule.get("enabled", False):
            pc = rule.get("protectedClass", "")
            if pc:
                enabled_classes.add(pc)

    if len(enabled_classes) == 0:
        return False

    # IntentCoverageMetric style — has `protectedClasses`
    protected_classes = record.get("protectedClasses")
    if isinstance(protected_classes, list):
        if any(pc in enabled_classes for pc in protected_classes):
            return True

    # AccuracyGoldenSetRecord / ConsistencyGoldenSetRecord style
    protected_class = record.get("protectedClass")
    if protected_class is not None:
        if protected_class in enabled_classes:
            return True

    # RealInputRecord style
    protected_class_hint = record.get("protectedClassHint")
    if protected_class_hint is not None:
        if protected_class_hint in enabled_classes:
            return True

    return False


# ─── enforceProtectionRules ─────────────────────────────────────────────────


def enforce_protection_rules(
    recommendations: list[dict[str, Any]],
    protected_case_rules: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Enforce protection rules across a set of recommendations.

    For any recommendation of type `reduce-retire-obsolete` that targets a
    protected record, the function ensures the recommendation is not left as a
    plain retirement unless it carries a governance-approved reason.

    When a protected retirement lacks governance approval the recommendation is
    re-typed to `no-update` and a warning is prepended to the `reason` field.
    The `actionability` is set to `protected-override`.

    Returns a new list — the input is not mutated.
    """
    enabled_classes: set[str] = set()
    for rule in protected_case_rules:
        if rule.get("enabled", False):
            pc = rule.get("protectedClass", "")
            if pc:
                enabled_classes.add(pc)

    result: list[dict[str, Any]] = []
    for rec in recommendations:
        if rec.get("type") != "reduce-retire-obsolete":
            result.append(rec)
            continue

        record_is_protected = (
            rec.get("isProtected", False)
            or any(
                pc in enabled_classes
                for pc in rec.get("protectedClasses", [])
            )
        )

        if not record_is_protected:
            result.append(rec)
            continue

        # Check for governance-approved reason
        reason = rec.get("reason", "")
        has_governance_approval = "governance-approved" in reason.lower()

        if has_governance_approval:
            result.append(rec)
            continue

        # Override: convert retirement to no-update with warning
        result.append({
            **rec,
            "type": "no-update",
            "actionability": "protected-override",
            "reason": f"[Protected case — retirement blocked] {reason}",
        })

    return result
