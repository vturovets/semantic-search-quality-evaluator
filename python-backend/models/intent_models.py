"""Pydantic models for the Canonical Intent Determination Engine."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from models.enums import IntentClass


class InputRecord(BaseModel):
    """Input record for intent determination. Maps to SRS §5.1."""

    model_config = ConfigDict(populate_by_name=True, by_alias=True)

    source_type: Literal["REAL", "ACCURACY", "CONSISTENCY"] = Field(alias="sourceType")
    source_id: str = Field(alias="sourceId")
    source_group_id: str | None = Field(default=None, alias="sourceGroupId")
    observed_at: str | None = Field(default=None, alias="observedAt")
    raw_text: str = Field(alias="rawText")
    sanitized_text: str = Field(alias="sanitizedText")
    expected_status: str | None = Field(default=None, alias="expectedStatus")
    expected_options: list[str] | None = Field(default=None, alias="expectedOptions")


class IntentDeterminationResult(BaseModel):
    """Structured output from the intent determination pipeline. Maps to SRS §5.3."""

    model_config = ConfigDict(populate_by_name=True, by_alias=True)

    source_id: str = Field(alias="sourceId")
    canonical_intent_id: str | None = Field(default=None, alias="canonicalIntentId")
    canonical_intent_label: str | None = Field(default=None, alias="canonicalIntentLabel")
    intent_class: IntentClass = Field(alias="intentClass")
    protected_class: str | None = Field(default=None, alias="protectedClass")
    normalized_status: str = Field(alias="normalizedStatus")
    normalized_option_signature: str = Field(alias="normalizedOptionSignature")
    comparison_anchor: str = Field(alias="comparisonAnchor")
    decision_method: str = Field(alias="decisionMethod")
    applied_rules: list[str] = Field(alias="appliedRules")
    ambiguity_flag: bool = Field(default=False, alias="ambiguityFlag")
    catalog_version: str = Field(alias="catalogVersion")
    sanitized_text: str = Field(alias="sanitizedText")
    error_message: str | None = Field(default=None, alias="errorMessage")
