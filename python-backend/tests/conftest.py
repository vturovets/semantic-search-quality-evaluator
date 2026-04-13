"""Shared pytest fixtures and Hypothesis custom strategies for all test files.

Provides reusable strategies for generating valid domain objects and shared
fixtures for storage instances used across property and unit tests.
"""

from __future__ import annotations

import tempfile
from typing import TYPE_CHECKING

import pytest
from hypothesis import strategies as st

from models.domain import (
    AnalysisRun,
    CanonicalIntent,
    ConfidenceInterval,
    DatasetImport,
    ExportArtifact,
    IntentCoverageMetric,
    IntentShareStabilityMetric,
    NormalizedRecord,
    OutcomeSignature,
    ParaphraseCoverageMetric,
    ProtectedCaseRule,
    Recommendation,
    RecommendationDecision,
    ValidationIssue,
)
from models.enums import VALID_TRANSITIONS
from models.requests import RecommendationFilters
from storage.file_backed import FileBackedStorage
from storage.memory import InMemoryStorage

if TYPE_CHECKING:
    from engine.priority_rules import PriorityInput

# ═══════════════════════════════════════════════════════════════════════════
# Primitive / building-block strategies
# ═══════════════════════════════════════════════════════════════════════════

id_st = st.text(
    alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyz0123456789-"),
    min_size=1,
    max_size=20,
)

iso_dt_st = st.just("2025-01-15T10:30:00Z")

nonempty_str_st = st.text(min_size=1, max_size=30).filter(lambda s: s.strip() != "")

# ═══════════════════════════════════════════════════════════════════════════
# Enum / Literal strategies
# ═══════════════════════════════════════════════════════════════════════════

dataset_type_st = st.sampled_from([
    "real-input", "accuracy-golden-set", "consistency-golden-set",
    "status-mapping", "reference-catalog",
])

intent_classification_st = st.sampled_from([
    "matched", "real-only", "golden-only", "underrepresented",
    "overrepresented", "candidate-obsolete", "protected-retained",
])

actionability_st = st.sampled_from([
    "action-ready", "monitor", "insufficient-evidence", "protected-override",
])

paraphrase_classification_st = st.sampled_from([
    "adequately-represented", "narrow", "missing", "protected-retained",
])

rec_type_st = st.sampled_from([
    "add-new-intent", "add-examples-for-intent", "add-paraphrase-variants",
    "create-paraphrase-group", "add-unsupported-coverage",
    "add-policy-pii-coverage", "reduce-retire-obsolete", "no-update",
])

rec_priority_st = st.sampled_from(["critical", "high", "medium", "low"])

rec_status_st = st.sampled_from([
    "draft", "analyst-reviewed", "po-review-pending", "approved",
    "rejected", "implemented", "archived",
])

protected_class_st = st.sampled_from([
    "policy-blocked", "pii-related", "non-english",
    "unsupported-intent", "rule-behavior-sensitive",
])

run_status_st = st.sampled_from([
    "created", "importing", "normalizing", "analyzing", "completed", "failed",
])

export_format_st = st.sampled_from(["markdown", "csv", "json"])

export_artifact_type_st = st.sampled_from([
    "run-summary", "recommendation-list", "intent-coverage-table",
    "wording-gap-table", "approval-register", "change-proposal",
])

golden_set_st = st.sampled_from(["accuracy", "consistency", "both"])

obs_window_st = st.sampled_from([7, 30, 90])

norm_method_st = st.sampled_from(["deterministic", "heuristic", "ai-assisted"])

intent_family_st = st.sampled_from(["billing", "account", "support", "general"])

# ═══════════════════════════════════════════════════════════════════════════
# Audit fields helper strategy
# ═══════════════════════════════════════════════════════════════════════════


def audit_fields_st():
    """Strategy producing a dict of audit field values suitable for unpacking."""
    return st.fixed_dictionaries({
        "id": id_st,
        "created_at": iso_dt_st,
        "created_by": nonempty_str_st,
        "updated_at": iso_dt_st,
        "version": st.integers(min_value=1, max_value=100),
        "source_ref": st.one_of(st.none(), nonempty_str_st),
    })


# ═══════════════════════════════════════════════════════════════════════════
# Domain object strategies
# ═══════════════════════════════════════════════════════════════════════════


@st.composite
def confidence_interval_st(draw):
    """Strategy for generating valid ConfidenceInterval objects."""
    lower = draw(st.floats(min_value=0.0, max_value=0.5, allow_nan=False, allow_infinity=False))
    upper = draw(st.floats(min_value=0.5, max_value=1.0, allow_nan=False, allow_infinity=False))
    return ConfidenceInterval(
        lower=lower,
        upper=upper,
        observed_share=draw(st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)),
        sample_size=draw(st.integers(min_value=1, max_value=10000)),
        confidence_level=0.95,
        method="wilson-score",
    )


@st.composite
def dataset_import_st(draw):
    """Strategy for generating valid DatasetImport objects."""
    af = draw(audit_fields_st())
    return DatasetImport(
        **af,
        import_id=draw(id_st),
        dataset_type=draw(dataset_type_st),
        file_name=draw(nonempty_str_st),
        record_count=draw(st.integers(min_value=0, max_value=10000)),
        validation_status=draw(st.sampled_from(["valid", "warnings", "rejected"])),
        validation_issues=[],
        parsed_at=draw(iso_dt_st),
    )


@st.composite
def analysis_run_st(draw):
    """Strategy for generating valid AnalysisRun objects."""
    af = draw(audit_fields_st())
    return AnalysisRun(
        **af,
        run_id=draw(id_st),
        name=draw(nonempty_str_st),
        status=draw(run_status_st),
        observation_window=draw(obs_window_st),
        real_input_dataset_id=draw(id_st),
        accuracy_golden_set_id=draw(id_st),
        consistency_golden_set_id=draw(id_st),
        reference_catalog_ids=[],
        materiality_threshold=0.05,
        min_sample_size=30,
        confidence_level=0.95,
        protected_case_rules=[],
        total_real_inputs=draw(st.integers(min_value=0, max_value=10000)),
        canonical_intent_count=draw(st.integers(min_value=0, max_value=500)),
        recommendation_count=draw(st.integers(min_value=0, max_value=500)),
        completed_at=None,
    )


@st.composite
def normalized_record_st(draw):
    """Strategy for generating valid NormalizedRecord objects with realistic fields."""
    af = draw(audit_fields_st())
    return NormalizedRecord(
        **af,
        original_source_id=draw(id_st),
        original_source_type=draw(dataset_type_st),
        original_values={"intent": draw(nonempty_str_st), "status": draw(nonempty_str_st)},
        normalized_intent=draw(nonempty_str_st),
        normalized_status=draw(nonempty_str_st),
        normalized_options=draw(st.lists(nonempty_str_st, max_size=3)),
        normalization_rule_id=draw(id_st),
        normalization_method=draw(norm_method_st),
        confidence=draw(st.one_of(
            st.none(),
            st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
        )),
        explanation=draw(st.one_of(st.none(), nonempty_str_st)),
    )


@st.composite
def coverage_metric_st(draw):
    """Strategy for generating valid IntentCoverageMetric objects."""
    af = draw(audit_fields_st())
    return IntentCoverageMetric(
        **af,
        run_id=draw(id_st),
        intent_id=draw(id_st),
        intent_label=draw(nonempty_str_st),
        intent_family=draw(intent_family_st),
        classification=draw(intent_classification_st),
        real_input_count=draw(st.integers(min_value=0, max_value=10000)),
        real_input_share_percent=draw(st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)),
        golden_set_case_count=draw(st.integers(min_value=0, max_value=10000)),
        golden_set_share_percent=draw(st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)),
        representation_delta=draw(st.floats(min_value=-100.0, max_value=100.0, allow_nan=False, allow_infinity=False)),
        is_protected=draw(st.booleans()),
        protected_classes=draw(st.lists(protected_class_st, max_size=2)),
        is_recommendation_candidate=draw(st.booleans()),
        confidence_interval=draw(confidence_interval_st()),
        actionability=draw(actionability_st),
    )


@st.composite
def stability_metric_st(draw):
    """Strategy for generating valid IntentShareStabilityMetric objects."""
    af = draw(audit_fields_st())
    return IntentShareStabilityMetric(
        **af,
        run_id=draw(id_st),
        intent_id=draw(id_st),
        observed_count=draw(st.integers(min_value=0, max_value=10000)),
        total_sample_size=draw(st.integers(min_value=1, max_value=10000)),
        observed_share=draw(st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)),
        confidence_interval=draw(confidence_interval_st()),
        materiality_threshold=draw(st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)),
        actionability=draw(actionability_st),
        meets_min_sample_size=draw(st.booleans()),
        rationale=draw(nonempty_str_st),
    )


@st.composite
def paraphrase_metric_st(draw):
    """Strategy for generating valid ParaphraseCoverageMetric objects."""
    af = draw(audit_fields_st())
    return ParaphraseCoverageMetric(
        **af,
        run_id=draw(id_st),
        intent_id=draw(id_st),
        paraphrase_group_id=draw(id_st),
        classification=draw(paraphrase_classification_st),
        golden_paraphrase_count=draw(st.integers(min_value=0, max_value=100)),
        real_wording_variant_count=draw(st.integers(min_value=0, max_value=100)),
        uncovered_variants=draw(st.lists(nonempty_str_st, max_size=3)),
        is_protected=draw(st.booleans()),
        has_instability_signal=draw(st.booleans()),
        outcome_variability=draw(st.lists(nonempty_str_st, max_size=3)),
    )


@st.composite
def recommendation_st(draw):
    """Strategy for generating valid Recommendation objects with realistic fields."""
    af = draw(audit_fields_st())
    return Recommendation(
        **af,
        recommendation_id=draw(id_st),
        run_id=draw(id_st),
        type=draw(rec_type_st),
        affected_golden_set=draw(golden_set_st),
        impacted_intent_id=draw(id_st),
        impacted_intent_family=draw(intent_family_st),
        reason=draw(nonempty_str_st),
        observed_frequency=draw(st.integers(min_value=0, max_value=10000)),
        observed_share_percent=draw(st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)),
        current_golden_representation=draw(st.integers(min_value=0, max_value=1000)),
        identified_gap=draw(nonempty_str_st),
        proposed_action=draw(nonempty_str_st),
        priority=draw(rec_priority_st),
        status=draw(rec_status_st),
        is_protected=draw(st.booleans()),
        protected_classes=draw(st.lists(protected_class_st, max_size=2)),
        actionability=draw(actionability_st),
        supporting_record_ids=draw(st.lists(id_st, max_size=3)),
        supporting_cluster_ids=draw(st.lists(id_st, max_size=3)),
    )


@st.composite
def recommendation_decision_st(draw):
    """Strategy for generating valid RecommendationDecision objects."""
    af = draw(audit_fields_st())
    return RecommendationDecision(
        **af,
        recommendation_id=draw(id_st),
        from_status=draw(rec_status_st),
        to_status=draw(rec_status_st),
        action=draw(st.sampled_from(["advance", "reject", "override"])),
        reason=draw(st.one_of(st.none(), nonempty_str_st)),
        decided_by=draw(nonempty_str_st),
        decided_at=draw(iso_dt_st),
        requires_ba_qa_approval=draw(st.booleans()),
        ba_qa_approved=draw(st.one_of(st.none(), st.booleans())),
    )


@st.composite
def export_artifact_st(draw):
    """Strategy for generating valid ExportArtifact objects."""
    af = draw(audit_fields_st())
    return ExportArtifact(
        **af,
        export_id=draw(id_st),
        run_id=draw(id_st),
        format=draw(export_format_st),
        artifacts=draw(st.lists(export_artifact_type_st, min_size=1, max_size=3)),
        generated_at=draw(iso_dt_st),
        pii_safe=draw(st.booleans()),
    )


@st.composite
def canonical_intent_st(draw):
    """Strategy for generating valid CanonicalIntent objects."""
    af = draw(audit_fields_st())
    outcome = OutcomeSignature(
        normalized_status="active",
        normalized_options=[],
        rule_behavior_markers=[],
        protected_class_markers=[],
    )
    return CanonicalIntent(
        **af,
        intent_id=draw(id_st),
        intent_label=draw(nonempty_str_st),
        intent_family=draw(intent_family_st),
        expected_business_meaning=draw(nonempty_str_st),
        expected_outcome_signature=outcome,
        is_protected=draw(st.booleans()),
        protected_classes=draw(st.lists(protected_class_st, max_size=2)),
        related_business_requirements=[],
        linked_accuracy_case_ids=[],
        linked_consistency_group_ids=[],
        linked_real_input_cluster_ids=[],
    )


# ═══════════════════════════════════════════════════════════════════════════
# Record strategies per dataset type
# ═══════════════════════════════════════════════════════════════════════════


@st.composite
def real_input_record_st(draw):
    """Strategy for generating a valid real-input record dict."""
    return {
        "recordId": draw(id_st),
        "query": draw(nonempty_str_st),
        "intent": draw(nonempty_str_st),
        "observedAt": draw(iso_dt_st),
    }


@st.composite
def accuracy_golden_set_record_st(draw):
    """Strategy for generating a valid accuracy-golden-set record dict."""
    return {
        "recordId": draw(id_st),
        "testCaseId": draw(id_st),
        "intent": draw(nonempty_str_st),
        "expectedStatus": draw(st.sampled_from(["active", "inactive", "pending"])),
        "expectedOptions": draw(nonempty_str_st),
    }


@st.composite
def consistency_golden_set_record_st(draw):
    """Strategy for generating a valid consistency-golden-set record dict."""
    return {
        "recordId": draw(id_st),
        "sourceTestCaseId": draw(id_st),
        "intent": draw(nonempty_str_st),
        "paraphraseText": draw(nonempty_str_st),
        "expectedStatus": draw(st.sampled_from(["active", "inactive", "pending"])),
        "expectedOptions": draw(nonempty_str_st),
    }


@st.composite
def status_mapping_record_st(draw):
    """Strategy for generating a valid status-mapping record dict."""
    return {
        "recordId": draw(id_st),
        "intent": draw(nonempty_str_st),
        "sourceStatus": draw(nonempty_str_st),
        "normalizedStatus": draw(nonempty_str_st),
    }


# ═══════════════════════════════════════════════════════════════════════════
# PriorityInput strategy
# ═══════════════════════════════════════════════════════════════════════════


def priority_input_st():
    """Strategy for generating valid PriorityInput values within valid ranges."""
    from engine.priority_rules import PriorityInput

    return st.builds(
        PriorityInput,
        observed_share_percent=st.floats(min_value=0, max_value=20, allow_nan=False),
        actionability=actionability_st,
        is_protected=st.booleans(),
        representation_delta=st.floats(min_value=-20, max_value=20, allow_nan=False),
        affects_governance=st.booleans(),
        affects_accuracy=st.booleans(),
        affects_consistency=st.booleans(),
    )


# ═══════════════════════════════════════════════════════════════════════════
# State machine strategies
# ═══════════════════════════════════════════════════════════════════════════

all_states_st = st.sampled_from(list(VALID_TRANSITIONS.keys()))


@st.composite
def valid_transition_st(draw):
    """Strategy for generating a valid (from_state, to_state) transition pair."""
    from_state = draw(all_states_st.filter(lambda s: len(VALID_TRANSITIONS[s]) > 0))
    to_state = draw(st.sampled_from(VALID_TRANSITIONS[from_state]))
    return (from_state, to_state)


@st.composite
def invalid_transition_st(draw):
    """Strategy for generating an invalid (from_state, to_state) transition pair."""
    from_state = draw(all_states_st)
    valid_targets = set(VALID_TRANSITIONS[from_state])
    all_statuses = set(VALID_TRANSITIONS.keys())
    invalid_targets = all_statuses - valid_targets
    if not invalid_targets:
        # All states are valid targets — pick from_state itself if not valid
        from_state = "archived"  # archived has no valid transitions
        invalid_targets = all_statuses
    to_state = draw(st.sampled_from(sorted(invalid_targets)))
    return (from_state, to_state)


# ═══════════════════════════════════════════════════════════════════════════
# RecommendationFilters strategy
# ═══════════════════════════════════════════════════════════════════════════


@st.composite
def recommendation_filters_st(draw):
    """Strategy for generating RecommendationFilters with optional fields."""
    return RecommendationFilters(
        type=draw(st.one_of(st.none(), rec_type_st)),
        priority=draw(st.one_of(st.none(), rec_priority_st)),
        status=draw(st.one_of(st.none(), rec_status_st)),
        protected_flag=draw(st.one_of(st.none(), st.booleans())),
        intent_family=draw(st.one_of(st.none(), intent_family_st)),
        golden_set=draw(st.one_of(st.none(), golden_set_st)),
    )


# ═══════════════════════════════════════════════════════════════════════════
# Shared pytest fixtures
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture
def in_memory_storage():
    """Return a fresh InMemoryStorage instance."""
    return InMemoryStorage()


@pytest.fixture
def file_backed_storage(tmp_path):
    """Return a FileBackedStorage instance backed by a temporary directory."""
    return FileBackedStorage(str(tmp_path))


@pytest.fixture(autouse=False)
def reset_storage():
    """Reset the global storage singleton before each test.

    Use this fixture when tests interact with the global ``get_storage()``
    factory to ensure isolation between tests.
    """
    import storage as storage_pkg

    storage_pkg._instance = None
    yield
    storage_pkg._instance = None


# ═══════════════════════════════════════════════════════════════════════════
# Intent Engine strategies (Requirements 11.1, 11.2)
# ═══════════════════════════════════════════════════════════════════════════

from models.intent_models import InputRecord
from engine.intent_config import (
    CatalogEntry,
    IntentEngineConfig,
    NormalizationConfig,
    ProtectedCaseConfig,
    StatusNormalizationConfig,
    OptionNormalizationConfig,
    DisambiguationRule,
)

_source_type_st = st.sampled_from(["REAL", "ACCURACY", "CONSISTENCY"])

_intent_class_st = st.sampled_from(["SUPPORTED", "UNSUPPORTED", "PROTECTED", "UNKNOWN"])

# Safe alphabet for regex patterns (no special regex chars)
_safe_word_st = st.text(
    alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyz"),
    min_size=2,
    max_size=10,
).filter(lambda s: s.strip() != "")


@st.composite
def input_record_st(draw):
    """Strategy for generating valid InputRecord objects with random source types,
    texts, and optional fields.

    **Validates: Requirements 11.1, 11.2**
    """
    sanitized = draw(nonempty_str_st)
    return InputRecord(
        sourceType=draw(_source_type_st),
        sourceId=draw(id_st),
        sourceGroupId=draw(st.one_of(st.none(), id_st)),
        rawText=sanitized,
        sanitizedText=sanitized,
        observedAt=draw(st.one_of(st.none(), iso_dt_st)),
        expectedStatus=draw(st.one_of(
            st.none(),
            st.sampled_from(["active", "inactive", "pending", "partial"]),
        )),
        expectedOptions=draw(st.one_of(
            st.none(),
            st.lists(nonempty_str_st, min_size=0, max_size=3),
        )),
    )


@st.composite
def catalog_entry_st(draw):
    """Strategy for generating valid CatalogEntry objects with random phrases,
    synonyms, and patterns.

    **Validates: Requirements 11.1, 11.2**
    """
    return CatalogEntry(
        intentId=draw(id_st),
        intentLabel=draw(nonempty_str_st),
        intentFamily=draw(intent_family_st),
        intentClass=draw(_intent_class_st),
        exactPhrases=draw(st.lists(_safe_word_st, min_size=1, max_size=3)),
        synonyms=draw(st.lists(_safe_word_st, min_size=0, max_size=3)),
        patterns=draw(st.lists(
            _safe_word_st.map(lambda w: f"\\b{w}\\b"),
            min_size=0,
            max_size=2,
        )),
        priorityScore=draw(st.floats(
            min_value=0.1, max_value=100.0,
            allow_nan=False, allow_infinity=False,
        )),
        protectedFlag=draw(st.booleans()),
        protectedClass=draw(st.one_of(st.none(), st.sampled_from([
            "policy-blocked", "pii-related", "non-english",
        ]))),
        defaultStatus=draw(st.one_of(st.none(), st.sampled_from([
            "MAPPED_AND_APPLIED", "PARTIALLY_APPLIED",
        ]))),
        defaultOptionSignature=draw(st.one_of(st.none(), nonempty_str_st)),
    )


@st.composite
def intent_engine_config_st(draw):
    """Strategy for generating a valid IntentEngineConfig with random catalog
    entries, normalization rules, and protected-case patterns.

    **Validates: Requirements 11.1, 11.2**
    """
    catalog = draw(st.lists(catalog_entry_st(), min_size=1, max_size=5))

    spelling_keys = draw(st.lists(_safe_word_st, min_size=0, max_size=3, unique=True))
    spelling_variants = {k: draw(_safe_word_st) for k in spelling_keys}

    return IntentEngineConfig(
        catalogVersion=draw(nonempty_str_st),
        catalog=catalog,
        protectedCase=ProtectedCaseConfig(
            policyBlockedPatterns=draw(st.lists(
                _safe_word_st.map(lambda w: f"\\b{w}\\b"),
                min_size=0, max_size=2,
            )),
            piiIndicators=draw(st.lists(
                _safe_word_st.map(lambda w: f"\\b{w}\\b"),
                min_size=0, max_size=2,
            )),
            nonEnglishPatterns=draw(st.lists(
                _safe_word_st.map(lambda w: f"\\b{w}\\b"),
                min_size=0, max_size=2,
            )),
            onMatch=draw(st.sampled_from(["terminate", "continue"])),
        ),
        normalization=NormalizationConfig(
            spellingVariants=spelling_variants,
            separatorReplacements=draw(st.sampled_from([
                {"-": " ", "_": " "},
                {"-": " "},
                {},
            ])),
            punctuationStripPattern=r"[^\w\s]",
        ),
        statusNormalization=StatusNormalizationConfig(
            canonicalStatuses=draw(st.sampled_from([
                {"active": "MAPPED_AND_APPLIED", "partial": "PARTIALLY_APPLIED"},
                {"active": "MAPPED_AND_APPLIED"},
                {},
            ])),
            defaultUnmapped="UNDETERMINED",
        ),
        optionNormalization=OptionNormalizationConfig(
            canonicalOptions=draw(st.sampled_from([
                {"all inclusive": "BOARDS:ALL_INCLUSIVE"},
                {},
            ])),
        ),
        disambiguationRules=draw(st.lists(
            st.builds(
                DisambiguationRule,
                ruleId=id_st,
                condition=st.just("highest_priority"),
                description=nonempty_str_st,
            ),
            min_size=0, max_size=2,
        )),
    )


@st.composite
def short_input_st(draw):
    """Strategy for generating InputRecord objects with ≤2 token sanitized_text,
    for short-input property tests.

    **Validates: Requirements 11.1, 11.2**
    """
    num_tokens = draw(st.integers(min_value=1, max_value=2))
    words = draw(st.lists(_safe_word_st, min_size=num_tokens, max_size=num_tokens))
    sanitized = " ".join(words)
    return InputRecord(
        sourceType=draw(_source_type_st),
        sourceId=draw(id_st),
        rawText=sanitized,
        sanitizedText=sanitized,
    )
