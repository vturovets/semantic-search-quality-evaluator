"""Property 23: Storage Round Trip

For any domain entity (run, import, normalized record, recommendation, decision,
export artifact), saving it to storage and then retrieving it should produce an
equivalent entity. This should hold for both InMemoryStorage and FileBackedStorage.

**Validates: Requirements 11.2, 11.3**
"""

from __future__ import annotations

import tempfile

import pytest
from hypothesis import given, settings, HealthCheck
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
from storage.file_backed import FileBackedStorage
from storage.memory import InMemoryStorage

# ─── Hypothesis Strategies ───────────────────────────────────────────────────

_id_st = st.text(
    alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyz0123456789-"),
    min_size=1,
    max_size=20,
)
_iso_dt = st.just("2025-01-15T10:30:00Z")
_nonempty_str = st.text(min_size=1, max_size=30).filter(lambda s: s.strip() != "")

_dataset_types = st.sampled_from([
    "real-input", "accuracy-golden-set", "consistency-golden-set",
    "status-mapping", "reference-catalog",
])
_intent_classifications = st.sampled_from([
    "matched", "real-only", "golden-only", "underrepresented",
    "overrepresented", "candidate-obsolete", "protected-retained",
])
_actionability = st.sampled_from([
    "action-ready", "monitor", "insufficient-evidence", "protected-override",
])
_paraphrase_classifications = st.sampled_from([
    "adequately-represented", "narrow", "missing", "protected-retained",
])
_rec_types = st.sampled_from([
    "add-new-intent", "add-examples-for-intent", "add-paraphrase-variants",
    "create-paraphrase-group", "add-unsupported-coverage",
    "add-policy-pii-coverage", "reduce-retire-obsolete", "no-update",
])
_rec_priorities = st.sampled_from(["critical", "high", "medium", "low"])
_rec_statuses = st.sampled_from([
    "draft", "analyst-reviewed", "po-review-pending", "approved",
    "rejected", "implemented", "archived",
])
_protected_classes = st.sampled_from([
    "policy-blocked", "pii-related", "non-english",
    "unsupported-intent", "rule-behavior-sensitive",
])
_run_statuses = st.sampled_from([
    "created", "importing", "normalizing", "analyzing", "completed", "failed",
])
_export_formats = st.sampled_from(["markdown", "csv", "json"])
_export_artifact_types = st.sampled_from([
    "run-summary", "recommendation-list", "intent-coverage-table",
    "wording-gap-table", "approval-register", "change-proposal",
])
_golden_set = st.sampled_from(["accuracy", "consistency", "both"])
_obs_windows = st.sampled_from([7, 30, 90])
_norm_methods = st.sampled_from(["deterministic", "heuristic", "ai-assisted"])


def _audit_fields():
    return st.fixed_dictionaries({
        "id": _id_st,
        "created_at": _iso_dt,
        "created_by": _nonempty_str,
        "updated_at": _iso_dt,
        "version": st.integers(min_value=1, max_value=100),
        "source_ref": st.one_of(st.none(), _nonempty_str),
    })


@st.composite
def _confidence_interval_st(draw):
    return ConfidenceInterval(
        lower=draw(st.floats(min_value=0.0, max_value=0.5, allow_nan=False, allow_infinity=False)),
        upper=draw(st.floats(min_value=0.5, max_value=1.0, allow_nan=False, allow_infinity=False)),
        observed_share=draw(st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)),
        sample_size=draw(st.integers(min_value=1, max_value=10000)),
        confidence_level=0.95,
        method="wilson-score",
    )


@st.composite
def _dataset_import_st(draw):
    af = draw(_audit_fields())
    return DatasetImport(
        **af,
        import_id=draw(_id_st),
        dataset_type=draw(_dataset_types),
        file_name=draw(_nonempty_str),
        record_count=draw(st.integers(min_value=0, max_value=10000)),
        validation_status=draw(st.sampled_from(["valid", "warnings", "rejected"])),
        validation_issues=[],
        parsed_at=draw(_iso_dt),
    )


@st.composite
def _analysis_run_st(draw):
    af = draw(_audit_fields())
    return AnalysisRun(
        **af,
        run_id=draw(_id_st),
        name=draw(_nonempty_str),
        status=draw(_run_statuses),
        observation_window=draw(_obs_windows),
        real_input_dataset_id=draw(_id_st),
        accuracy_golden_set_id=draw(_id_st),
        consistency_golden_set_id=draw(_id_st),
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
def _normalized_record_st(draw):
    af = draw(_audit_fields())
    return NormalizedRecord(
        **af,
        original_source_id=draw(_id_st),
        original_source_type=draw(_dataset_types),
        original_values={"intent": "test"},
        normalized_intent=draw(_nonempty_str),
        normalized_status=draw(_nonempty_str),
        normalized_options=[],
        normalization_rule_id=draw(_id_st),
        normalization_method=draw(_norm_methods),
        confidence=None,
        explanation=None,
    )


@st.composite
def _recommendation_st(draw):
    af = draw(_audit_fields())
    return Recommendation(
        **af,
        recommendation_id=draw(_id_st),
        run_id=draw(_id_st),
        type=draw(_rec_types),
        affected_golden_set=draw(_golden_set),
        impacted_intent_id=draw(_id_st),
        impacted_intent_family=draw(_nonempty_str),
        reason=draw(_nonempty_str),
        observed_frequency=draw(st.integers(min_value=0, max_value=10000)),
        observed_share_percent=draw(st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)),
        current_golden_representation=draw(st.integers(min_value=0, max_value=1000)),
        identified_gap=draw(_nonempty_str),
        proposed_action=draw(_nonempty_str),
        priority=draw(_rec_priorities),
        status=draw(_rec_statuses),
        is_protected=draw(st.booleans()),
        protected_classes=draw(st.lists(_protected_classes, max_size=2)),
        actionability=draw(_actionability),
        supporting_record_ids=[],
        supporting_cluster_ids=[],
    )


@st.composite
def _decision_st(draw):
    af = draw(_audit_fields())
    return RecommendationDecision(
        **af,
        recommendation_id=draw(_id_st),
        from_status=draw(_rec_statuses),
        to_status=draw(_rec_statuses),
        action=draw(st.sampled_from(["advance", "reject", "override"])),
        reason=draw(st.one_of(st.none(), _nonempty_str)),
        decided_by=draw(_nonempty_str),
        decided_at=draw(_iso_dt),
        requires_ba_qa_approval=draw(st.booleans()),
        ba_qa_approved=draw(st.one_of(st.none(), st.booleans())),
    )


@st.composite
def _export_artifact_st(draw):
    af = draw(_audit_fields())
    return ExportArtifact(
        **af,
        export_id=draw(_id_st),
        run_id=draw(_id_st),
        format=draw(_export_formats),
        artifacts=draw(st.lists(_export_artifact_types, min_size=1, max_size=3)),
        generated_at=draw(_iso_dt),
        pii_safe=draw(st.booleans()),
    )


@st.composite
def _coverage_metric_st(draw):
    af = draw(_audit_fields())
    return IntentCoverageMetric(
        **af,
        run_id=draw(_id_st),
        intent_id=draw(_id_st),
        intent_label=draw(_nonempty_str),
        intent_family=draw(_nonempty_str),
        classification=draw(_intent_classifications),
        real_input_count=draw(st.integers(min_value=0, max_value=10000)),
        real_input_share_percent=draw(st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)),
        golden_set_case_count=draw(st.integers(min_value=0, max_value=10000)),
        golden_set_share_percent=draw(st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)),
        representation_delta=draw(st.floats(min_value=-100.0, max_value=100.0, allow_nan=False, allow_infinity=False)),
        is_protected=draw(st.booleans()),
        protected_classes=draw(st.lists(_protected_classes, max_size=2)),
        is_recommendation_candidate=draw(st.booleans()),
        confidence_interval=draw(_confidence_interval_st()),
        actionability=draw(_actionability),
    )


@st.composite
def _stability_metric_st(draw):
    af = draw(_audit_fields())
    return IntentShareStabilityMetric(
        **af,
        run_id=draw(_id_st),
        intent_id=draw(_id_st),
        observed_count=draw(st.integers(min_value=0, max_value=10000)),
        total_sample_size=draw(st.integers(min_value=1, max_value=10000)),
        observed_share=draw(st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)),
        confidence_interval=draw(_confidence_interval_st()),
        materiality_threshold=draw(st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)),
        actionability=draw(_actionability),
        meets_min_sample_size=draw(st.booleans()),
        rationale=draw(_nonempty_str),
    )


@st.composite
def _paraphrase_metric_st(draw):
    af = draw(_audit_fields())
    return ParaphraseCoverageMetric(
        **af,
        run_id=draw(_id_st),
        intent_id=draw(_id_st),
        paraphrase_group_id=draw(_id_st),
        classification=draw(_paraphrase_classifications),
        golden_paraphrase_count=draw(st.integers(min_value=0, max_value=100)),
        real_wording_variant_count=draw(st.integers(min_value=0, max_value=100)),
        uncovered_variants=[],
        is_protected=draw(st.booleans()),
        has_instability_signal=draw(st.booleans()),
        outcome_variability=[],
    )


@st.composite
def _canonical_intent_st(draw):
    af = draw(_audit_fields())
    outcome = OutcomeSignature(
        normalized_status="active",
        normalized_options=[],
        rule_behavior_markers=[],
        protected_class_markers=[],
    )
    return CanonicalIntent(
        **af,
        intent_id=draw(_id_st),
        intent_label=draw(_nonempty_str),
        intent_family=draw(_nonempty_str),
        expected_business_meaning=draw(_nonempty_str),
        expected_outcome_signature=outcome,
        is_protected=draw(st.booleans()),
        protected_classes=draw(st.lists(_protected_classes, max_size=2)),
        related_business_requirements=[],
        linked_accuracy_case_ids=[],
        linked_consistency_group_ids=[],
        linked_real_input_cluster_ids=[],
    )


# ─── Storage factory fixtures ───────────────────────────────────────────────

def _make_in_memory():
    return InMemoryStorage()


def _make_file_backed():
    tmp = tempfile.mkdtemp()
    return FileBackedStorage(tmp)


STORAGE_FACTORIES = [_make_in_memory, _make_file_backed]


# ─── Property Tests ─────────────────────────────────────────────────────────
# Feature: python-analysis-backend, Property 23: Storage Round Trip


@pytest.mark.parametrize("make_storage", STORAGE_FACTORIES)
@given(data=st.data())
@settings(max_examples=100, database=None)
async def test_import_roundtrip(make_storage, data):
    """Saving a DatasetImport and retrieving it produces an equivalent entity."""
    storage = make_storage()
    imp = data.draw(_dataset_import_st())
    await storage.save_import(imp)
    retrieved = await storage.get_import(imp.import_id)
    assert retrieved is not None
    assert retrieved.model_dump(by_alias=True) == imp.model_dump(by_alias=True)


@pytest.mark.parametrize("make_storage", STORAGE_FACTORIES)
@given(data=st.data())
@settings(max_examples=100, database=None)
async def test_run_roundtrip(make_storage, data):
    """Saving an AnalysisRun and retrieving it produces an equivalent entity."""
    storage = make_storage()
    run = data.draw(_analysis_run_st())
    await storage.save_run(run)
    retrieved = await storage.get_run(run.run_id)
    assert retrieved is not None
    assert retrieved.model_dump(by_alias=True) == run.model_dump(by_alias=True)


@pytest.mark.parametrize("make_storage", STORAGE_FACTORIES)
@given(data=st.data())
@settings(max_examples=100, database=None)
async def test_run_list_roundtrip(make_storage, data):
    """Saving runs and listing them returns all saved runs."""
    storage = make_storage()
    run = data.draw(_analysis_run_st())
    await storage.save_run(run)
    runs = await storage.list_runs()
    assert len(runs) >= 1
    run_ids = [r.run_id for r in runs]
    assert run.run_id in run_ids


@pytest.mark.parametrize("make_storage", STORAGE_FACTORIES)
@given(data=st.data())
@settings(max_examples=100, database=None)
async def test_normalized_records_roundtrip(make_storage, data):
    """Saving normalized records and retrieving them produces equivalent entities."""
    storage = make_storage()
    run_id = data.draw(_id_st)
    records = data.draw(st.lists(_normalized_record_st(), min_size=1, max_size=5))
    await storage.save_normalized_records(run_id, records)
    retrieved = await storage.get_normalized_records(run_id)
    assert len(retrieved) == len(records)
    for orig, ret in zip(records, retrieved):
        assert ret.model_dump(by_alias=True) == orig.model_dump(by_alias=True)


@pytest.mark.parametrize("make_storage", STORAGE_FACTORIES)
@given(data=st.data())
@settings(max_examples=100, database=None)
async def test_recommendation_roundtrip(make_storage, data):
    """Saving recommendations and retrieving them produces equivalent entities."""
    storage = make_storage()
    run_id = data.draw(_id_st)
    recs = data.draw(st.lists(_recommendation_st(), min_size=1, max_size=5))
    await storage.save_recommendations(run_id, recs)
    retrieved = await storage.get_recommendations(run_id)
    assert len(retrieved) == len(recs)
    for orig, ret in zip(recs, retrieved):
        assert ret.model_dump(by_alias=True) == orig.model_dump(by_alias=True)


@pytest.mark.parametrize("make_storage", STORAGE_FACTORIES)
@given(data=st.data())
@settings(max_examples=100, database=None)
async def test_decision_roundtrip(make_storage, data):
    """Saving a decision and retrieving it produces an equivalent entity."""
    storage = make_storage()
    decision = data.draw(_decision_st())
    await storage.save_decision(decision)
    retrieved = await storage.get_decisions(decision.recommendation_id)
    assert len(retrieved) == 1
    assert retrieved[0].model_dump(by_alias=True) == decision.model_dump(by_alias=True)


@pytest.mark.parametrize("make_storage", STORAGE_FACTORIES)
@given(data=st.data())
@settings(max_examples=100, database=None)
async def test_export_artifact_roundtrip(make_storage, data):
    """Saving an export artifact and retrieving it produces an equivalent entity."""
    storage = make_storage()
    artifact = data.draw(_export_artifact_st())
    await storage.save_export_artifact(artifact)
    retrieved = await storage.get_export_artifacts(artifact.run_id)
    assert len(retrieved) == 1
    assert retrieved[0].model_dump(by_alias=True) == artifact.model_dump(by_alias=True)


@pytest.mark.parametrize("make_storage", STORAGE_FACTORIES)
@given(data=st.data())
@settings(max_examples=100, database=None)
async def test_coverage_metrics_roundtrip(make_storage, data):
    """Saving coverage metrics and retrieving them produces equivalent entities."""
    storage = make_storage()
    run_id = data.draw(_id_st)
    metrics = data.draw(st.lists(_coverage_metric_st(), min_size=1, max_size=5))
    await storage.save_coverage_metrics(run_id, metrics)
    retrieved = await storage.get_coverage_metrics(run_id)
    assert len(retrieved) == len(metrics)
    for orig, ret in zip(metrics, retrieved):
        assert ret.model_dump(by_alias=True) == orig.model_dump(by_alias=True)


@pytest.mark.parametrize("make_storage", STORAGE_FACTORIES)
@given(data=st.data())
@settings(max_examples=100, database=None)
async def test_stability_metrics_roundtrip(make_storage, data):
    """Saving stability metrics and retrieving them produces equivalent entities."""
    storage = make_storage()
    run_id = data.draw(_id_st)
    metrics = data.draw(st.lists(_stability_metric_st(), min_size=1, max_size=5))
    await storage.save_stability_metrics(run_id, metrics)
    retrieved = await storage.get_stability_metrics(run_id)
    assert len(retrieved) == len(metrics)
    for orig, ret in zip(metrics, retrieved):
        assert ret.model_dump(by_alias=True) == orig.model_dump(by_alias=True)


@pytest.mark.parametrize("make_storage", STORAGE_FACTORIES)
@given(data=st.data())
@settings(max_examples=100, database=None)
async def test_paraphrase_metrics_roundtrip(make_storage, data):
    """Saving paraphrase metrics and retrieving them produces equivalent entities."""
    storage = make_storage()
    run_id = data.draw(_id_st)
    metrics = data.draw(st.lists(_paraphrase_metric_st(), min_size=1, max_size=5))
    await storage.save_paraphrase_metrics(run_id, metrics)
    retrieved = await storage.get_paraphrase_metrics(run_id)
    assert len(retrieved) == len(metrics)
    for orig, ret in zip(metrics, retrieved):
        assert ret.model_dump(by_alias=True) == orig.model_dump(by_alias=True)


@pytest.mark.parametrize("make_storage", STORAGE_FACTORIES)
@given(data=st.data())
@settings(max_examples=100, database=None)
async def test_canonical_intents_roundtrip(make_storage, data):
    """Saving canonical intents and retrieving them produces equivalent entities."""
    storage = make_storage()
    run_id = data.draw(_id_st)
    intents = data.draw(st.lists(_canonical_intent_st(), min_size=1, max_size=5))
    await storage.save_canonical_intents(run_id, intents)
    retrieved = await storage.get_canonical_intents(run_id)
    assert len(retrieved) == len(intents)
    for orig, ret in zip(intents, retrieved):
        assert ret.model_dump(by_alias=True) == orig.model_dump(by_alias=True)


@pytest.mark.parametrize("make_storage", STORAGE_FACTORIES)
@given(data=st.data())
@settings(max_examples=100, database=None)
async def test_imported_records_roundtrip(make_storage, data):
    """Saving raw imported records and retrieving them produces equivalent data."""
    storage = make_storage()
    import_id = data.draw(_id_st)
    records = data.draw(st.lists(
        st.fixed_dictionaries({"key": _nonempty_str, "value": _nonempty_str}),
        min_size=1,
        max_size=5,
    ))
    await storage.save_imported_records(import_id, records)
    retrieved = await storage.get_imported_records(import_id)
    assert retrieved == records


@pytest.mark.parametrize("make_storage", STORAGE_FACTORIES)
async def test_get_nonexistent_returns_none_or_empty(make_storage):
    """Getting a non-existent entity returns None or empty list."""
    storage = make_storage()
    assert await storage.get_import("nonexistent") is None
    assert await storage.get_run("nonexistent") is None
    assert await storage.get_normalized_records("nonexistent") == []
    assert await storage.get_recommendations("nonexistent") == []
    assert await storage.get_decisions("nonexistent") == []
    assert await storage.get_export_artifacts("nonexistent") == []
    assert await storage.get_canonical_intents("nonexistent") == []
    assert await storage.get_coverage_metrics("nonexistent") == []
    assert await storage.get_stability_metrics("nonexistent") == []
    assert await storage.get_paraphrase_metrics("nonexistent") == []
    assert await storage.get_imported_records("nonexistent") == []
