"""Normalization Engine — port of lib/quality-evaluation/normalization.ts.

Deterministic rule-table-first normalization with full audit trail.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal


# ─── Rule Table Types ───────────────────────────────────────────────────────


@dataclass
class NormalizationRuleTable:
    id: str
    intent_synonyms: dict[str, str]
    status_aliases: dict[str, str]
    option_normalization: dict[str, str]


# ─── Default Rule Table ─────────────────────────────────────────────────────

DEFAULT_RULE_TABLE = NormalizationRuleTable(
    id="default-rule-table-v1",
    intent_synonyms={
        # product search synonyms
        "product-search": "product-search",
        "product_search": "product-search",
        "productsearch": "product-search",
        "search-product": "product-search",
        "item-search": "product-search",
        "find-product": "product-search",
        # price filter synonyms
        "price-filter": "price-filter",
        "price_filter": "price-filter",
        "pricefilter": "price-filter",
        "filter-by-price": "price-filter",
        "price-range": "price-filter",
        "budget-filter": "price-filter",
        # color filter synonyms
        "color-filter": "color-filter",
        "color_filter": "color-filter",
        "colorfilter": "color-filter",
        "filter-by-color": "color-filter",
        "colour-filter": "color-filter",
        # size filter synonyms
        "size-filter": "size-filter",
        "size_filter": "size-filter",
        "sizefilter": "size-filter",
        "filter-by-size": "size-filter",
        # brand filter synonyms
        "brand-filter": "brand-filter",
        "brand_filter": "brand-filter",
        "brandfilter": "brand-filter",
        "filter-by-brand": "brand-filter",
        # sort by rating synonyms
        "sort-by-rating": "sort-by-rating",
        "sort_by_rating": "sort-by-rating",
        "rating-sort": "sort-by-rating",
        "best-rated": "sort-by-rating",
        "top-rated": "sort-by-rating",
        # return policy synonyms
        "return-policy": "return-policy",
        "return_policy": "return-policy",
        "returns": "return-policy",
        "refund-policy": "return-policy",
        # gift wrap synonyms
        "gift-wrap": "gift-wrap",
        "gift_wrap": "gift-wrap",
        "giftwrap": "gift-wrap",
        "gift-wrapping": "gift-wrap",
        # protected intents
        "pii-address-lookup": "pii-address-lookup",
        "pii_address_lookup": "pii-address-lookup",
        "address-lookup": "pii-address-lookup",
        "policy-blocked-content": "policy-blocked-content",
        "policy_blocked_content": "policy-blocked-content",
        "blocked-content": "policy-blocked-content",
        "non-english-query": "non-english-query",
        "non_english_query": "non-english-query",
        "non-english": "non-english-query",
        "unsupported-intent": "unsupported-intent",
        "unsupported_intent": "unsupported-intent",
        "unsupported": "unsupported-intent",
        "dedup-conflict-resolution": "dedup-conflict-resolution",
        "dedup_conflict_resolution": "dedup-conflict-resolution",
        "conflict-resolution": "dedup-conflict-resolution",
        "negation-handling": "dedup-conflict-resolution",
    },
    status_aliases={
        "results-found": "results-found",
        "results_found": "results-found",
        "found": "results-found",
        "success": "results-found",
        "info-displayed": "info-displayed",
        "info_displayed": "info-displayed",
        "info": "info-displayed",
        "information-shown": "info-displayed",
        "option-applied": "option-applied",
        "option_applied": "option-applied",
        "applied": "option-applied",
        "pii-redacted": "pii-redacted",
        "pii_redacted": "pii-redacted",
        "redacted": "pii-redacted",
        "blocked": "blocked",
        "policy-blocked": "blocked",
        "restricted": "blocked",
        "unsupported": "unsupported",
        "not-supported": "unsupported",
        "not_supported": "unsupported",
        "no-results": "no-results",
        "no_results": "no-results",
        "empty": "no-results",
    },
    option_normalization={
        # category normalization
        "category:shoe": "category:shoes",
        "category:boot": "category:boots",
        "category:jacket": "category:jackets",
        "category:dress": "category:dresses",
        "category:backpack": "category:backpacks",
        "category:tshirt": "category:tshirts",
        "category:t-shirt": "category:tshirts",
        "category:earbud": "category:earbuds",
        "category:bottle": "category:bottles",
        "category:yoga-mat": "category:yoga-mats",
        "category:sneaker": "category:sneakers",
        # color normalization
        "color:blue": "color:blue",
        "color:navy": "color:navy",
        "color:navy-blue": "color:navy",
        "color:red": "color:red",
        "color:green": "color:green",
        "color:forest-green": "color:green",
        "color:pink": "color:pink",
        "color:coral-pink": "color:pink",
        "color:burgundy": "color:burgundy",
        "color:white": "color:white",
        "color:black": "color:black",
        # size normalization
        "size:extra-large": "size:xl",
        "size:x-large": "size:xl",
        "size:xlarge": "size:xl",
        "size:large": "size:large",
        "size:lg": "size:large",
        "size:medium": "size:medium",
        "size:md": "size:medium",
        "size:small": "size:small",
        "size:sm": "size:small",
        # sort normalization
        "sort:rating": "sort:rating-desc",
        "sort:top-rated": "sort:rating-desc",
        "sort:popularity": "sort:popularity-desc",
        "sort:most-popular": "sort:popularity-desc",
        # gift wrap normalization
        "gift-wrap:true": "gift-wrap:yes",
        "gift-wrap:1": "gift-wrap:yes",
        "gift-note:true": "gift-note:yes",
        "gift-note:1": "gift-note:yes",
    },
)


# ─── Helpers ────────────────────────────────────────────────────────────────

_counter = 0


def _generate_id() -> str:
    global _counter
    _counter += 1
    return f"norm-{int(time.time() * 1000)}-{_counter}"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _make_audit(id_: str) -> dict[str, Any]:
    now = _now_iso()
    return {
        "id": id_,
        "createdAt": now,
        "createdBy": "normalization-engine",
        "updatedAt": now,
        "version": 1,
    }


# ─── Intent Normalization ───────────────────────────────────────────────────


@dataclass
class _NormResult:
    value: str
    method: Literal["deterministic", "heuristic"]
    explanation: str


def normalize_intent(
    raw: str | None,
    rule_table: NormalizationRuleTable,
) -> _NormResult:
    if not raw or raw.strip() == "":
        return _NormResult(
            value="unknown",
            method="heuristic",
            explanation='No intent provided; defaulted to "unknown".',
        )

    key = raw.strip().lower()

    # Exact match in synonym table
    if key in rule_table.intent_synonyms:
        canonical = rule_table.intent_synonyms[key]
        return _NormResult(
            value=canonical,
            method="deterministic",
            explanation=f'Mapped intent "{raw}" to "{canonical}" via rule table "{rule_table.id}".',
        )

    # Heuristic: pass through as-is (lowercase, trimmed)
    return _NormResult(
        value=key,
        method="heuristic",
        explanation=f'No rule-table match for intent "{raw}"; kept as "{key}" (heuristic pass-through).',
    )


# ─── Status Normalization ───────────────────────────────────────────────────


def normalize_status(
    raw: str | None,
    rule_table: NormalizationRuleTable,
) -> _NormResult:
    if not raw or raw.strip() == "":
        return _NormResult(
            value="unknown",
            method="heuristic",
            explanation='No status provided; defaulted to "unknown".',
        )

    key = raw.strip().lower()

    if key in rule_table.status_aliases:
        canonical = rule_table.status_aliases[key]
        return _NormResult(
            value=canonical,
            method="deterministic",
            explanation=f'Mapped status "{raw}" to "{canonical}" via rule table "{rule_table.id}".',
        )

    return _NormResult(
        value=key,
        method="heuristic",
        explanation=f'No rule-table match for status "{raw}"; kept as "{key}" (heuristic pass-through).',
    )


# ─── Option Normalization ───────────────────────────────────────────────────


@dataclass
class _OptionsNormResult:
    values: list[str]
    method: Literal["deterministic", "heuristic"]
    explanation: str


def normalize_options(
    raw: list[str] | None,
    rule_table: NormalizationRuleTable,
) -> _OptionsNormResult:
    if not raw or len(raw) == 0:
        return _OptionsNormResult(
            values=[],
            method="deterministic",
            explanation="No options to normalize.",
        )

    all_deterministic = True
    heuristic_items: list[str] = []
    normalized: list[str] = []

    for opt in raw:
        key = opt.strip().lower()
        if key in rule_table.option_normalization:
            normalized.append(rule_table.option_normalization[key])
        else:
            all_deterministic = False
            heuristic_items.append(opt)
            normalized.append(key)

    # Deduplicate while preserving order
    seen: set[str] = set()
    deduped: list[str] = []
    for v in normalized:
        if v not in seen:
            seen.add(v)
            deduped.append(v)

    method: Literal["deterministic", "heuristic"] = "deterministic" if all_deterministic else "heuristic"
    if all_deterministic:
        explanation = f'All {len(raw)} option(s) normalized via rule table "{rule_table.id}".'
    else:
        matched = len(raw) - len(heuristic_items)
        explanation = (
            f"{matched}/{len(raw)} option(s) matched rule table; "
            f"{len(heuristic_items)} kept as-is: [{', '.join(heuristic_items)}]."
        )

    return _OptionsNormResult(values=deduped, method=method, explanation=explanation)


# ─── Record Field Extraction per Dataset Type ───────────────────────────────


@dataclass
class _ExtractedFields:
    source_id: str
    raw_intent: str | None
    raw_status: str | None
    raw_options: list[str] | None
    original_values: dict[str, str]


def extract_fields(
    record: dict[str, Any],
    dataset_type: str,
) -> _ExtractedFields:
    if dataset_type == "real-input":
        source_id = str(record.get("recordId") or record.get("id") or "")
        raw_intent = record.get("canonicalIntent")
        raw_status = record.get("semanticOutcomeStatus")
        raw_options = record.get("appliedOptions")
        original_values: dict[str, str] = {}
        if record.get("recordId"):
            original_values["recordId"] = str(record["recordId"])
        if record.get("canonicalIntent"):
            original_values["canonicalIntent"] = str(record["canonicalIntent"])
        if record.get("semanticOutcomeStatus"):
            original_values["semanticOutcomeStatus"] = str(record["semanticOutcomeStatus"])
        if record.get("appliedOptions"):
            original_values["appliedOptions"] = ", ".join(record["appliedOptions"])
        if record.get("sanitizedText"):
            original_values["sanitizedText"] = str(record["sanitizedText"])
        return _ExtractedFields(
            source_id=source_id,
            raw_intent=raw_intent,
            raw_status=raw_status,
            raw_options=raw_options,
            original_values=original_values,
        )

    elif dataset_type == "accuracy-golden-set":
        source_id = str(record.get("testCaseId") or record.get("id") or "")
        raw_intent = record.get("canonicalIntent")
        raw_status = record.get("expectedStatus")
        raw_options = record.get("expectedOptions")
        original_values = {}
        if record.get("testCaseId"):
            original_values["testCaseId"] = str(record["testCaseId"])
        if record.get("canonicalIntent"):
            original_values["canonicalIntent"] = str(record["canonicalIntent"])
        if record.get("expectedStatus"):
            original_values["expectedStatus"] = str(record["expectedStatus"])
        if record.get("expectedOptions"):
            original_values["expectedOptions"] = ", ".join(record["expectedOptions"])
        if record.get("freeTextInput"):
            original_values["freeTextInput"] = str(record["freeTextInput"])
        return _ExtractedFields(
            source_id=source_id,
            raw_intent=raw_intent,
            raw_status=raw_status,
            raw_options=raw_options,
            original_values=original_values,
        )

    elif dataset_type == "consistency-golden-set":
        source_id = str(record.get("variantId") or record.get("id") or "")
        raw_intent = record.get("canonicalIntent")
        raw_status = record.get("expectedStatus")
        raw_options = record.get("expectedOptions")
        original_values = {}
        if record.get("variantId"):
            original_values["variantId"] = str(record["variantId"])
        if record.get("sourceTestCaseId"):
            original_values["sourceTestCaseId"] = str(record["sourceTestCaseId"])
        if record.get("canonicalIntent"):
            original_values["canonicalIntent"] = str(record["canonicalIntent"])
        if record.get("expectedStatus"):
            original_values["expectedStatus"] = str(record["expectedStatus"])
        if record.get("expectedOptions"):
            original_values["expectedOptions"] = ", ".join(record["expectedOptions"])
        if record.get("freeTextInput"):
            original_values["freeTextInput"] = str(record["freeTextInput"])
        return _ExtractedFields(
            source_id=source_id,
            raw_intent=raw_intent,
            raw_status=raw_status,
            raw_options=raw_options,
            original_values=original_values,
        )

    elif dataset_type == "status-mapping":
        source_id = str(record.get("statusCode") or "")
        raw_intent = None
        raw_status = record.get("statusCode")
        raw_options = None
        original_values = {}
        if record.get("statusCode"):
            original_values["statusCode"] = str(record["statusCode"])
        if record.get("businessMeaning"):
            original_values["businessMeaning"] = str(record["businessMeaning"])
        if record.get("statusClass"):
            original_values["statusClass"] = str(record["statusClass"])
        return _ExtractedFields(
            source_id=source_id,
            raw_intent=raw_intent,
            raw_status=raw_status,
            raw_options=raw_options,
            original_values=original_values,
        )

    else:
        # reference-catalog or unknown: generic extraction
        id_ = str(record.get("id") or record.get("recordId") or record.get("testCaseId") or "")
        intent = record.get("canonicalIntent") or record.get("intent")
        status = record.get("status") or record.get("expectedStatus") or record.get("semanticOutcomeStatus")
        opts = record.get("options") or record.get("expectedOptions") or record.get("appliedOptions")
        original_values = {}
        for k, v in record.items():
            if v is not None:
                original_values[k] = str(v)
        return _ExtractedFields(
            source_id=id_,
            raw_intent=intent if isinstance(intent, str) else None,
            raw_status=status if isinstance(status, str) else None,
            raw_options=opts if isinstance(opts, list) else None,
            original_values=original_values,
        )


# ─── Public API ─────────────────────────────────────────────────────────────


def normalize_record(
    record: dict[str, Any],
    dataset_type: str,
    rule_table: NormalizationRuleTable | None = None,
) -> dict[str, Any]:
    """Normalize a single source record into a NormalizedRecord dict with full audit trail.

    Applies deterministic rule-table mappings first (intent synonyms, status aliases,
    option normalization). Falls back to heuristic pass-through for unmapped values.
    """
    if rule_table is None:
        rule_table = DEFAULT_RULE_TABLE

    fields = extract_fields(record, dataset_type)

    intent_result = normalize_intent(fields.raw_intent, rule_table)
    status_result = normalize_status(fields.raw_status, rule_table)
    options_result = normalize_options(fields.raw_options, rule_table)

    # Overall method: deterministic only if ALL sub-normalizations were deterministic
    if (
        intent_result.method == "deterministic"
        and status_result.method == "deterministic"
        and options_result.method == "deterministic"
    ):
        overall_method: Literal["deterministic", "heuristic"] = "deterministic"
    else:
        overall_method = "heuristic"

    explanation_parts = [
        intent_result.explanation,
        status_result.explanation,
        options_result.explanation,
    ]

    id_ = _generate_id()
    audit = _make_audit(id_)

    return {
        **audit,
        "originalSourceId": fields.source_id,
        "originalSourceType": dataset_type,
        "originalValues": fields.original_values,
        "normalizedIntent": intent_result.value,
        "normalizedStatus": status_result.value,
        "normalizedOptions": options_result.values,
        "normalizationRuleId": rule_table.id,
        "normalizationMethod": overall_method,
        "confidence": 1.0 if overall_method == "deterministic" else 0.7,
        "explanation": " ".join(explanation_parts),
    }


def normalize_dataset(
    records: list[dict[str, Any]],
    dataset_type: str,
    rule_table: NormalizationRuleTable | None = None,
) -> list[dict[str, Any]]:
    """Normalize an array of source records into NormalizedRecord dicts.

    Each record is independently normalized with its own audit trail.
    """
    if rule_table is None:
        rule_table = DEFAULT_RULE_TABLE
    return [normalize_record(record, dataset_type, rule_table) for record in records]
