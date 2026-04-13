"""Runtime validation schemas — port of lib/quality-evaluation/schemas.ts.

Plain Python validators (no external library beyond typing).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ─── Validation Result ───────────────────────────────────────────────────────


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)


# ─── Enum Value Sets ────────────────────────────────────────────────────────

OBSERVATION_WINDOWS: list[int] = [7, 30, 90]

DATASET_TYPES: list[str] = [
    "real-input",
    "accuracy-golden-set",
    "consistency-golden-set",
    "status-mapping",
    "reference-catalog",
]

PROTECTED_CLASSES: list[str] = [
    "policy-blocked",
    "pii-related",
    "non-english",
    "unsupported-intent",
    "rule-behavior-sensitive",
]

EXPORT_FORMATS: list[str] = ["markdown", "csv", "json"]

EXPORT_ARTIFACT_TYPES: list[str] = [
    "run-summary",
    "recommendation-list",
    "intent-coverage-table",
    "wording-gap-table",
    "approval-register",
    "change-proposal",
]

RECOMMENDATION_PRIORITIES: list[str] = ["critical", "high", "medium", "low"]

RECOMMENDATION_STATUSES: list[str] = [
    "draft",
    "analyst-reviewed",
    "po-review-pending",
    "approved",
    "rejected",
    "implemented",
    "archived",
]

APPROVER_ROLES: list[str] = ["analyst", "ba_qa", "po"]
APPROVAL_ACTIONS: list[str] = ["approve", "reject"]


# ─── Helpers ────────────────────────────────────────────────────────────────


def is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and len(value.strip()) > 0


def is_string(value: Any) -> bool:
    return isinstance(value, str)


def is_number(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    return isinstance(value, (int, float)) and not (isinstance(value, float) and (value != value))


def is_array(value: Any) -> bool:
    return isinstance(value, list)


def is_object(value: Any) -> bool:
    return isinstance(value, dict)


def is_string_array(value: Any) -> bool:
    return is_array(value) and all(isinstance(v, str) for v in value)


# ─── Import Payload Validators ──────────────────────────────────────────────


def validate_real_input_record(data: Any) -> ValidationResult:
    """Validate a real-input record payload."""
    errors: list[str] = []
    if not is_object(data):
        return ValidationResult(valid=False, errors=["Payload must be an object"])

    # Required fields
    if not is_non_empty_string(data.get("recordId")):
        errors.append("recordId is required and must be a non-empty string")
    if not is_non_empty_string(data.get("observedAt")):
        errors.append("observedAt is required and must be a non-empty string")
    if not is_non_empty_string(data.get("sanitizedText")):
        errors.append("sanitizedText is required and must be a non-empty string")

    # Optional typed fields
    if "sourceChannel" in data and data["sourceChannel"] is not None:
        if not is_string(data["sourceChannel"]):
            errors.append("sourceChannel must be a string")
    if "region" in data and data["region"] is not None:
        if not is_string(data["region"]):
            errors.append("region must be a string")
    if "canonicalIntent" in data and data["canonicalIntent"] is not None:
        if not is_string(data["canonicalIntent"]):
            errors.append("canonicalIntent must be a string")
    if "semanticOutcomeStatus" in data and data["semanticOutcomeStatus"] is not None:
        if not is_string(data["semanticOutcomeStatus"]):
            errors.append("semanticOutcomeStatus must be a string")
    if "appliedOptions" in data and data["appliedOptions"] is not None:
        if not is_string_array(data["appliedOptions"]):
            errors.append("appliedOptions must be an array of strings")
    if "protectedClassHint" in data and data["protectedClassHint"] is not None:
        val = data["protectedClassHint"]
        if not is_string(val) or val not in PROTECTED_CLASSES:
            errors.append(f"protectedClassHint must be one of: {', '.join(PROTECTED_CLASSES)}")
    if "frequency" in data and data["frequency"] is not None:
        val = data["frequency"]
        if not is_number(val) or val < 0:
            errors.append("frequency must be a non-negative number")

    return ValidationResult(valid=len(errors) == 0, errors=errors)


def validate_accuracy_golden_set_record(data: Any) -> ValidationResult:
    """Validate an accuracy golden set record payload."""
    errors: list[str] = []
    if not is_object(data):
        return ValidationResult(valid=False, errors=["Payload must be an object"])

    if not is_non_empty_string(data.get("testCaseId")):
        errors.append("testCaseId is required and must be a non-empty string")
    if not is_non_empty_string(data.get("businessRequirement")):
        errors.append("businessRequirement is required and must be a non-empty string")
    if not is_non_empty_string(data.get("scenario")):
        errors.append("scenario is required and must be a non-empty string")
    if not is_non_empty_string(data.get("freeTextInput")):
        errors.append("freeTextInput is required and must be a non-empty string")
    if not is_string_array(data.get("expectedOptions")):
        errors.append("expectedOptions is required and must be an array of strings")
    if not is_non_empty_string(data.get("expectedStatus")):
        errors.append("expectedStatus is required and must be a non-empty string")
    if not is_non_empty_string(data.get("canonicalIntent")):
        errors.append("canonicalIntent is required and must be a non-empty string")
    if not is_non_empty_string(data.get("goldenSetVersion")):
        errors.append("goldenSetVersion is required and must be a non-empty string")

    if "protectedClass" in data and data["protectedClass"] is not None:
        val = data["protectedClass"]
        if not is_string(val) or val not in PROTECTED_CLASSES:
            errors.append(f"protectedClass must be one of: {', '.join(PROTECTED_CLASSES)}")

    return ValidationResult(valid=len(errors) == 0, errors=errors)


def validate_consistency_golden_set_record(data: Any) -> ValidationResult:
    """Validate a consistency golden set record payload."""
    errors: list[str] = []
    if not is_object(data):
        return ValidationResult(valid=False, errors=["Payload must be an object"])

    if not is_non_empty_string(data.get("sourceTestCaseId")):
        errors.append("sourceTestCaseId is required and must be a non-empty string")
    if not is_non_empty_string(data.get("variantId")):
        errors.append("variantId is required and must be a non-empty string")
    if not is_non_empty_string(data.get("businessRequirement")):
        errors.append("businessRequirement is required and must be a non-empty string")
    if not is_non_empty_string(data.get("scenario")):
        errors.append("scenario is required and must be a non-empty string")
    if not is_non_empty_string(data.get("freeTextInput")):
        errors.append("freeTextInput is required and must be a non-empty string")
    if not is_string_array(data.get("expectedOptions")):
        errors.append("expectedOptions is required and must be an array of strings")
    if not is_non_empty_string(data.get("expectedStatus")):
        errors.append("expectedStatus is required and must be a non-empty string")
    if not is_non_empty_string(data.get("canonicalIntent")):
        errors.append("canonicalIntent is required and must be a non-empty string")
    if not is_non_empty_string(data.get("goldenSetVersion")):
        errors.append("goldenSetVersion is required and must be a non-empty string")

    if "protectedClass" in data and data["protectedClass"] is not None:
        val = data["protectedClass"]
        if not is_string(val) or val not in PROTECTED_CLASSES:
            errors.append(f"protectedClass must be one of: {', '.join(PROTECTED_CLASSES)}")

    return ValidationResult(valid=len(errors) == 0, errors=errors)


def validate_status_mapping_record(data: Any) -> ValidationResult:
    """Validate a status mapping record payload."""
    errors: list[str] = []
    if not is_object(data):
        return ValidationResult(valid=False, errors=["Payload must be an object"])

    if not is_non_empty_string(data.get("statusCode")):
        errors.append("statusCode is required and must be a non-empty string")
    if not is_non_empty_string(data.get("businessMeaning")):
        errors.append("businessMeaning is required and must be a non-empty string")
    if not is_non_empty_string(data.get("statusClass")):
        errors.append("statusClass is required and must be a non-empty string")

    if "priorityWeight" in data and data["priorityWeight"] is not None:
        val = data["priorityWeight"]
        if not is_number(val) or val < 0:
            errors.append("priorityWeight must be a non-negative number")

    return ValidationResult(valid=len(errors) == 0, errors=errors)


# ─── Dispatch validator by dataset type ─────────────────────────────────────


def validate_import_record(data: Any, dataset_type: str) -> ValidationResult:
    """Validate a single import record based on dataset type."""
    if dataset_type == "real-input":
        return validate_real_input_record(data)
    elif dataset_type == "accuracy-golden-set":
        return validate_accuracy_golden_set_record(data)
    elif dataset_type == "consistency-golden-set":
        return validate_consistency_golden_set_record(data)
    elif dataset_type == "status-mapping":
        return validate_status_mapping_record(data)
    elif dataset_type == "reference-catalog":
        # Reference catalogs are loosely typed; just require an object
        if not is_object(data):
            return ValidationResult(valid=False, errors=["Payload must be an object"])
        return ValidationResult(valid=True, errors=[])
    else:
        return ValidationResult(valid=False, errors=[f"Unknown dataset type: {dataset_type}"])
