"""Public API for the Canonical Intent Determination Engine.

Provides ``IntentDeterminationService`` — the single entry-point for
classifying input records through the 8-stage pipeline.

Requirements: 13.1, 13.2, 13.3, 13.4, 14.1, 14.2, 15.4
"""

from __future__ import annotations

from engine.intent_config import IntentEngineConfig
from engine.intent_pipeline import (
    PipelineState,
    build_anchor,
    detect_unsupported,
    disambiguate,
    handle_unknown,
    match_supported,
    normalize_outcome,
    normalize_text,
    route_protected,
)
from models.intent_models import InputRecord, IntentDeterminationResult


class IntentDeterminationService:
    """Orchestrates the 8-stage intent determination pipeline.

    Usage::

        svc = IntentDeterminationService(config)
        result = svc.determine(record)
        results = svc.determine_batch(records)
    """

    def __init__(self, config: IntentEngineConfig) -> None:
        self._config = config

    # ── Single-record API (Req 14.1, 14.2) ──────────────────────────────

    def determine(self, record: InputRecord) -> IntentDeterminationResult:
        """Run the full 8-stage pipeline for a single *record*."""
        state = PipelineState(record=record)

        stages = [
            normalize_text,
            route_protected,
            match_supported,
            disambiguate,
            detect_unsupported,
            handle_unknown,
            normalize_outcome,
            build_anchor,
        ]

        for stage in stages:
            try:
                state = stage(state, self._config)
            except Exception as exc:  # noqa: BLE001
                state = PipelineState(
                    record=record,
                    intent_class="UNKNOWN",
                    error_message=str(exc),
                    decision_method="error",
                    normalized_text=state.normalized_text,
                    applied_rules=state.applied_rules,
                )
                break

        return self._to_result(state)

    # ── Batch API (Req 13.1, 13.2, 13.3, 13.4) ─────────────────────────

    def determine_batch(
        self, records: list[InputRecord]
    ) -> list[IntentDeterminationResult]:
        """Process a list of records, isolating per-record failures."""
        results: list[IntentDeterminationResult] = []
        for record in records:
            try:
                results.append(self.determine(record))
            except Exception as exc:  # noqa: BLE001
                results.append(
                    IntentDeterminationResult(
                        source_id=record.source_id,
                        intent_class="UNKNOWN",
                        normalized_status="UNDETERMINED",
                        normalized_option_signature="",
                        comparison_anchor=f"UNKNOWN | UNDETERMINED | {record.sanitized_text}",
                        decision_method="error",
                        applied_rules=["error:batch_processing"],
                        catalog_version=self._config.catalog_version,
                        sanitized_text=record.sanitized_text,
                        error_message=str(exc),
                    )
                )
        return results

    # ── Config hot-reload (Req 15.4) ─────────────────────────────────────

    def reload_config(self, config: IntentEngineConfig) -> None:
        """Replace the active configuration with *config*.

        Pydantic validation runs during construction of ``IntentEngineConfig``,
        so if *config* was built from untrusted data the caller should catch
        ``ValidationError``.  This method raises ``ValueError`` when the
        supplied object is not a valid ``IntentEngineConfig``.
        """
        if not isinstance(config, IntentEngineConfig):
            raise ValueError("config must be a valid IntentEngineConfig instance")
        self._config = config

    # ── Internal helpers ─────────────────────────────────────────────────

    def _to_result(self, state: PipelineState) -> IntentDeterminationResult:
        """Map final ``PipelineState`` to an ``IntentDeterminationResult``."""
        return IntentDeterminationResult(
            source_id=state.record.source_id,
            canonical_intent_id=state.canonical_intent_id,
            canonical_intent_label=state.canonical_intent_label,
            intent_class=state.intent_class or "UNKNOWN",
            protected_class=state.protected_class,
            normalized_status=state.normalized_status or "UNDETERMINED",
            normalized_option_signature=state.normalized_option_signature or "",
            comparison_anchor=state.comparison_anchor
            or f"UNKNOWN | UNDETERMINED | {state.record.sanitized_text}",
            decision_method=state.decision_method or "unknown",
            applied_rules=state.applied_rules if state.applied_rules else ["default:no_rules_applied"],
            ambiguity_flag=state.ambiguity_flag,
            catalog_version=self._config.catalog_version,
            sanitized_text=state.record.sanitized_text,
            error_message=state.error_message,
        )
