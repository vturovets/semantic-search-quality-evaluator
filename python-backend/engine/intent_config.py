"""Configuration models for the Canonical Intent Determination Engine.

All models are loaded from external configuration sources (Requirements 15.1–15.3)
and carry a catalog_version for reproducibility (Requirement 17.1).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from models.enums import IntentClass


# ─── Catalog Entry ──────────────────────────────────────────────────────────


class CatalogEntry(BaseModel):
    """A single entry in the intent catalog."""

    model_config = ConfigDict(populate_by_name=True, by_alias=True)

    intent_id: str = Field(alias="intentId")
    intent_label: str = Field(alias="intentLabel")
    intent_family: str = Field(alias="intentFamily")
    intent_class: IntentClass = Field(alias="intentClass")
    exact_phrases: list[str] = Field(alias="exactPhrases")
    synonyms: list[str] = Field(alias="synonyms")
    patterns: list[str] = Field(alias="patterns")  # regex patterns
    priority_score: float = Field(alias="priorityScore")
    protected_flag: bool = Field(alias="protectedFlag")
    protected_class: str | None = Field(default=None, alias="protectedClass")
    default_status: str | None = Field(default=None, alias="defaultStatus")
    default_option_signature: str | None = Field(default=None, alias="defaultOptionSignature")


# ─── Protected-Case Config ──────────────────────────────────────────────────


class ProtectedCaseConfig(BaseModel):
    """Rules for protected-case routing (Requirement 15.3)."""

    model_config = ConfigDict(populate_by_name=True, by_alias=True)

    policy_blocked_patterns: list[str] = Field(alias="policyBlockedPatterns")
    pii_indicators: list[str] = Field(alias="piiIndicators")
    non_english_patterns: list[str] = Field(alias="nonEnglishPatterns")
    on_match: Literal["terminate", "continue"] = Field(alias="onMatch")


# ─── Normalization Config ───────────────────────────────────────────────────


class NormalizationConfig(BaseModel):
    """Text normalization rules (Requirement 15.2)."""

    model_config = ConfigDict(populate_by_name=True, by_alias=True)

    spelling_variants: dict[str, str] = Field(alias="spellingVariants")
    separator_replacements: dict[str, str] = Field(alias="separatorReplacements")
    punctuation_strip_pattern: str = Field(alias="punctuationStripPattern")


# ─── Status Normalization Config ────────────────────────────────────────────


class StatusNormalizationConfig(BaseModel):
    """Status value normalization rules."""

    model_config = ConfigDict(populate_by_name=True, by_alias=True)

    canonical_statuses: dict[str, str] = Field(alias="canonicalStatuses")
    default_unmapped: str = Field(default="UNDETERMINED", alias="defaultUnmapped")


# ─── Option Normalization Config ────────────────────────────────────────────


class OptionNormalizationConfig(BaseModel):
    """Option value normalization rules."""

    model_config = ConfigDict(populate_by_name=True, by_alias=True)

    canonical_options: dict[str, str] = Field(alias="canonicalOptions")


# ─── Disambiguation Rule ────────────────────────────────────────────────────


class DisambiguationRule(BaseModel):
    """A single disambiguation rule for resolving multi-match situations."""

    model_config = ConfigDict(populate_by_name=True, by_alias=True)

    rule_id: str = Field(alias="ruleId")
    condition: str = Field(alias="condition")
    description: str = Field(alias="description")


# ─── Top-Level Engine Config ────────────────────────────────────────────────


class IntentEngineConfig(BaseModel):
    """Top-level configuration for the intent determination engine.

    Loaded from an external source (Requirement 15.1) and versioned
    for reproducibility (Requirement 17.1).
    """

    model_config = ConfigDict(populate_by_name=True, by_alias=True)

    catalog_version: str = Field(alias="catalogVersion")
    catalog: list[CatalogEntry] = Field(alias="catalog")
    protected_case: ProtectedCaseConfig = Field(alias="protectedCase")
    normalization: NormalizationConfig = Field(alias="normalization")
    status_normalization: StatusNormalizationConfig = Field(alias="statusNormalization")
    option_normalization: OptionNormalizationConfig = Field(alias="optionNormalization")
    disambiguation_rules: list[DisambiguationRule] = Field(alias="disambiguationRules")
