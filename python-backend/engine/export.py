"""Export Module — port of lib/quality-evaluation/export.ts.

Generates Markdown, CSV, and JSON exports with PII filtering.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any


# ─── PII Filtering ──────────────────────────────────────────────────────────

PII_FIELDS: list[str] = [
    "sanitizedText",
    "freeTextInput",
    "originalValues",
]


def strip_pii(data: Any) -> Any:
    """Recursively strip PII-sensitive fields from an object or array."""
    if data is None:
        return data
    if isinstance(data, list):
        return [strip_pii(item) for item in data]
    if isinstance(data, dict):
        result: dict[str, Any] = {}
        for key, value in data.items():
            if key in PII_FIELDS:
                continue
            result[key] = strip_pii(value)
        return result
    return data


# ─── Markdown Export ────────────────────────────────────────────────────────


def export_markdown(
    run: dict[str, Any],
    metrics: dict[str, Any],
    recommendations: list[dict[str, Any]],
) -> str:
    """Generate a Markdown report with sections for: run summary, coverage metrics,
    recommendations by priority, and protected cases."""
    lines: list[str] = []

    # Title
    lines.append(f"# Quality Evaluation Report: {run.get('name', '')}")
    lines.append("")

    # Run Summary
    lines.append("## Run Summary")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| Run ID | {run.get('runId', '')} |")
    lines.append(f"| Status | {run.get('status', '')} |")
    lines.append(f"| Observation Window | {metrics.get('observationWindow', '')} days |")
    lines.append(f"| Real Inputs Analyzed | {metrics.get('realInputsAnalyzed', '')} |")
    lines.append(f"| Canonical Intents Found | {metrics.get('canonicalIntentsFound', '')} |")
    lines.append(f"| Materiality Threshold | {metrics.get('materialityThreshold', '')} |")
    lines.append(f"| Confidence Level | {metrics.get('confidenceLevel', '')} |")
    meets = metrics.get("meetsMinSampleSize", False)
    lines.append(f"| Meets Min Sample Size | {'Yes' if meets else 'No'} |")
    lines.append("")

    # Coverage Metrics
    lines.append("## Coverage Metrics")
    lines.append("")
    lines.append("| Metric | Count |")
    lines.append("| --- | --- |")
    lines.append(f"| Matched Intents | {metrics.get('matchedIntents', 0)} |")
    lines.append(f"| Real-Only Intents | {metrics.get('realOnlyIntents', 0)} |")
    lines.append(f"| Golden-Only Intents | {metrics.get('goldenOnlyIntents', 0)} |")
    lines.append(f"| Underrepresented Intents | {metrics.get('underrepresentedIntents', 0)} |")
    lines.append(f"| Overrepresented Intents | {metrics.get('overrepresentedIntents', 0)} |")
    lines.append(f"| Candidate Obsolete Intents | {metrics.get('candidateObsoleteIntents', 0)} |")
    lines.append(f"| Action-Ready Intents | {metrics.get('actionReadyIntents', 0)} |")
    lines.append(f"| Monitor Intents | {metrics.get('monitorIntents', 0)} |")
    lines.append(f"| Insufficient Evidence Intents | {metrics.get('insufficientEvidenceIntents', 0)} |")
    lines.append(f"| Accuracy Intents Covered | {metrics.get('accuracyIntentsCovered', 0)} |")
    lines.append(f"| Consistency Groups Reviewed | {metrics.get('consistencyGroupsReviewed', 0)} |")
    lines.append(f"| Narrow Paraphrase Groups | {metrics.get('narrowParaphraseGroups', 0)} |")
    lines.append("")

    # Recommendations by Priority
    lines.append("## Recommendations by Priority")
    lines.append("")

    priorities = ["critical", "high", "medium", "low"]
    for priority in priorities:
        filtered = [r for r in recommendations if r.get("priority") == priority]
        if len(filtered) == 0:
            continue

        cap = priority[0].upper() + priority[1:]
        lines.append(f"### {cap} ({len(filtered)})")
        lines.append("")
        lines.append("| ID | Type | Intent | Gap | Action |")
        lines.append("| --- | --- | --- | --- | --- |")
        for rec in filtered:
            lines.append(
                f"| {rec.get('recommendationId', '')} "
                f"| {rec.get('type', '')} "
                f"| {rec.get('impactedIntentId', '')} "
                f"| {rec.get('identifiedGap', '')} "
                f"| {rec.get('proposedAction', '')} |"
            )
        lines.append("")

    # Protected Cases
    protected_recs = [r for r in recommendations if r.get("isProtected", False)]
    lines.append("## Protected Cases")
    lines.append("")
    if len(protected_recs) == 0:
        lines.append("No protected cases in this run.")
    else:
        lines.append("| ID | Type | Intent | Protected Classes | Status |")
        lines.append("| --- | --- | --- | --- | --- |")
        for rec in protected_recs:
            pc = ", ".join(rec.get("protectedClasses", []))
            lines.append(
                f"| {rec.get('recommendationId', '')} "
                f"| {rec.get('type', '')} "
                f"| {rec.get('impactedIntentId', '')} "
                f"| {pc} "
                f"| {rec.get('status', '')} |"
            )
    lines.append("")

    return "\n".join(lines)


# ─── CSV Export ─────────────────────────────────────────────────────────────


def escape_csv_field(value: Any) -> str:
    """Escape a CSV field value: wrap in quotes if it contains commas, quotes, or newlines."""
    s = "" if value is None else str(value)
    if "," in s or '"' in s or "\n" in s:
        return f'"{s.replace(chr(34), chr(34) + chr(34))}"'
    return s


def get_csv_headers(artifact_type: str) -> list[str]:
    """Get the column headers for a given artifact type."""
    headers_map: dict[str, list[str]] = {
        "run-summary": ["field", "value"],
        "recommendation-list": [
            "recommendationId", "runId", "type", "affectedGoldenSet",
            "impactedIntentId", "impactedIntentFamily", "reason",
            "observedFrequency", "observedSharePercent", "currentGoldenRepresentation",
            "identifiedGap", "proposedAction", "priority", "status",
            "isProtected", "protectedClasses", "actionability",
        ],
        "intent-coverage-table": [
            "intentId", "intentLabel", "intentFamily", "classification",
            "realInputCount", "realInputSharePercent", "goldenSetCaseCount",
            "goldenSetSharePercent", "representationDelta", "isProtected",
            "protectedClasses", "actionability",
        ],
        "wording-gap-table": [
            "intentId", "paraphraseGroupId", "classification",
            "goldenParaphraseCount", "realWordingVariantCount",
            "uncoveredVariants", "isProtected", "hasInstabilitySignal",
            "outcomeVariability",
        ],
        "approval-register": [
            "recommendationId", "fromStatus", "toStatus", "action",
            "reason", "decidedBy", "decidedAt", "requiresBaQaApproval",
            "baQaApproved",
        ],
        "change-proposal": [
            "recommendationId", "type", "affectedGoldenSet",
            "impactedIntentId", "identifiedGap", "proposedAction",
            "priority", "status", "isProtected",
        ],
    }
    return headers_map.get(artifact_type, [])


def flatten_value(value: Any) -> str:
    """Flatten a value for CSV output (arrays become semicolon-separated)."""
    if isinstance(value, list):
        return "; ".join(str(v) for v in value)
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return ""
    return str(value)


def export_csv(data: list[Any], artifact_type: str) -> str:
    """Generate CSV string for any exportable artifact type.
    PII fields are stripped before export."""
    safe_data = strip_pii(data)
    headers = get_csv_headers(artifact_type)

    if len(headers) == 0 or len(safe_data) == 0:
        return ",".join(headers) + "\n"

    lines: list[str] = []
    lines.append(",".join(escape_csv_field(h) for h in headers))

    for row in safe_data:
        if not isinstance(row, dict):
            continue
        values = [escape_csv_field(flatten_value(row.get(h))) for h in headers]
        lines.append(",".join(values))

    return "\n".join(lines) + "\n"


# ─── JSON Export ────────────────────────────────────────────────────────────


def export_json(data: list[Any], artifact_type: str) -> str:
    """Generate JSON string for any exportable artifact type.
    PII fields are stripped before export."""
    safe_data = strip_pii(data)
    return json.dumps(
        {
            "artifactType": artifact_type,
            "exportedAt": datetime.now(timezone.utc).isoformat(),
            "recordCount": len(safe_data),
            "data": safe_data,
        },
        indent=2,
    )
