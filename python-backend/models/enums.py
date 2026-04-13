"""Literal types and constants matching lib/quality-evaluation/types.ts."""

from typing import Literal

# ─── Enums and Literal Types ────────────────────────────────────────────────

ObservationWindow = Literal[7, 30, 90]

DatasetType = Literal[
    "real-input",
    "accuracy-golden-set",
    "consistency-golden-set",
    "status-mapping",
    "reference-catalog",
]

IntentClass = Literal["SUPPORTED", "UNSUPPORTED", "PROTECTED", "UNKNOWN"]

IntentClassification = Literal[
    "matched",
    "real-only",
    "golden-only",
    "underrepresented",
    "overrepresented",
    "candidate-obsolete",
    "protected-retained",
]

ActionabilityClassification = Literal[
    "action-ready",
    "monitor",
    "insufficient-evidence",
    "protected-override",
]

ParaphraseClassification = Literal[
    "adequately-represented",
    "narrow",
    "missing",
    "protected-retained",
]

RecommendationType = Literal[
    "add-new-intent",
    "add-examples-for-intent",
    "add-paraphrase-variants",
    "create-paraphrase-group",
    "add-unsupported-coverage",
    "add-policy-pii-coverage",
    "reduce-retire-obsolete",
    "no-update",
]

RecommendationPriority = Literal["critical", "high", "medium", "low"]

RecommendationStatus = Literal[
    "draft",
    "analyst-reviewed",
    "po-review-pending",
    "approved",
    "rejected",
    "implemented",
    "archived",
]

ProtectedClass = Literal[
    "policy-blocked",
    "pii-related",
    "non-english",
    "unsupported-intent",
    "rule-behavior-sensitive",
]

RunStatus = Literal[
    "created",
    "importing",
    "normalizing",
    "analyzing",
    "completed",
    "failed",
]

ExportFormat = Literal["markdown", "csv", "json"]

ExportArtifactType = Literal[
    "run-summary",
    "recommendation-list",
    "intent-coverage-table",
    "wording-gap-table",
    "approval-register",
    "change-proposal",
]

# ─── State Machine (FR-12) ─────────────────────────────────────────────────

VALID_TRANSITIONS: dict[str, list[str]] = {
    "draft": ["analyst-reviewed"],
    "analyst-reviewed": ["po-review-pending", "rejected"],
    "po-review-pending": ["approved", "rejected", "analyst-reviewed"],
    "approved": ["implemented", "archived"],
    "rejected": ["archived", "draft"],
    "implemented": ["archived"],
    "archived": [],
}
