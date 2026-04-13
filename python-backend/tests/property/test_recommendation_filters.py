"""Property 24: Recommendation Filter Application

For any set of stored recommendations and any combination of filter parameters
(type, priority, status, protectedFlag, intentFamily, goldenSet), the filtered
result should contain exactly those recommendations matching all specified filter criteria.

**Validates: Requirements 11.4**
"""

from __future__ import annotations

import tempfile

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from models.domain import Recommendation
from models.requests import RecommendationFilters
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
_actionability = st.sampled_from([
    "action-ready", "monitor", "insufficient-evidence", "protected-override",
])
_golden_set = st.sampled_from(["accuracy", "consistency", "both"])
_intent_families = st.sampled_from(["billing", "account", "support", "general"])


@st.composite
def _recommendation_st(draw):
    return Recommendation(
        id=draw(_id_st),
        created_at=draw(_iso_dt),
        created_by="system",
        updated_at=draw(_iso_dt),
        version=1,
        source_ref=None,
        recommendation_id=draw(_id_st),
        run_id=draw(_id_st),
        type=draw(_rec_types),
        affected_golden_set=draw(_golden_set),
        impacted_intent_id=draw(_id_st),
        impacted_intent_family=draw(_intent_families),
        reason="test reason",
        observed_frequency=draw(st.integers(min_value=0, max_value=10000)),
        observed_share_percent=draw(st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)),
        current_golden_representation=draw(st.integers(min_value=0, max_value=1000)),
        identified_gap="test gap",
        proposed_action="test action",
        priority=draw(_rec_priorities),
        status=draw(_rec_statuses),
        is_protected=draw(st.booleans()),
        protected_classes=draw(st.lists(_protected_classes, max_size=2)),
        actionability=draw(_actionability),
        supporting_record_ids=[],
        supporting_cluster_ids=[],
    )


@st.composite
def _filters_st(draw):
    return RecommendationFilters(
        type=draw(st.one_of(st.none(), _rec_types)),
        priority=draw(st.one_of(st.none(), _rec_priorities)),
        status=draw(st.one_of(st.none(), _rec_statuses)),
        protected_flag=draw(st.one_of(st.none(), st.booleans())),
        intent_family=draw(st.one_of(st.none(), _intent_families)),
        golden_set=draw(st.one_of(st.none(), _golden_set)),
    )


def _matches_filters(rec: Recommendation, filters: RecommendationFilters) -> bool:
    """Reference implementation: check if a recommendation matches all filter criteria."""
    if filters.type is not None and rec.type != filters.type:
        return False
    if filters.priority is not None and rec.priority != filters.priority:
        return False
    if filters.status is not None and rec.status != filters.status:
        return False
    if filters.protected_flag is not None and rec.is_protected != filters.protected_flag:
        return False
    if filters.intent_family is not None and rec.impacted_intent_family != filters.intent_family:
        return False
    if filters.golden_set is not None and rec.affected_golden_set != filters.golden_set:
        return False
    return True


# ─── Storage factory fixtures ───────────────────────────────────────────────

def _make_in_memory():
    return InMemoryStorage()


def _make_file_backed():
    tmp = tempfile.mkdtemp()
    return FileBackedStorage(tmp)


STORAGE_FACTORIES = [_make_in_memory, _make_file_backed]


# ─── Property Tests ─────────────────────────────────────────────────────────
# Feature: python-analysis-backend, Property 24: Recommendation Filter Application


@pytest.mark.parametrize("make_storage", STORAGE_FACTORIES)
@given(data=st.data())
@settings(max_examples=100)
async def test_recommendation_filter_correctness(make_storage, data):
    """Filtered results contain exactly those recommendations matching all filter criteria."""
    storage = make_storage()
    run_id = data.draw(_id_st)
    recs = data.draw(st.lists(_recommendation_st(), min_size=0, max_size=10))
    filters = data.draw(_filters_st())

    await storage.save_recommendations(run_id, recs)
    filtered = await storage.get_recommendations(run_id, filters)

    # Compute expected result using reference implementation
    expected = [r for r in recs if _matches_filters(r, filters)]

    assert len(filtered) == len(expected)
    filtered_ids = {r.recommendation_id for r in filtered}
    expected_ids = {r.recommendation_id for r in expected}
    # Since recommendation_ids may not be unique in generated data,
    # compare by serialized form
    filtered_dicts = [r.model_dump(by_alias=True) for r in filtered]
    expected_dicts = [r.model_dump(by_alias=True) for r in expected]
    assert filtered_dicts == expected_dicts


@pytest.mark.parametrize("make_storage", STORAGE_FACTORIES)
@given(data=st.data())
@settings(max_examples=100)
async def test_no_filters_returns_all(make_storage, data):
    """When no filters are applied, all recommendations are returned."""
    storage = make_storage()
    run_id = data.draw(_id_st)
    recs = data.draw(st.lists(_recommendation_st(), min_size=0, max_size=10))

    await storage.save_recommendations(run_id, recs)
    retrieved = await storage.get_recommendations(run_id, None)

    assert len(retrieved) == len(recs)


@pytest.mark.parametrize("make_storage", STORAGE_FACTORIES)
@given(data=st.data())
@settings(max_examples=100)
async def test_empty_filters_returns_all(make_storage, data):
    """When all filter fields are None, all recommendations are returned."""
    storage = make_storage()
    run_id = data.draw(_id_st)
    recs = data.draw(st.lists(_recommendation_st(), min_size=0, max_size=10))
    empty_filters = RecommendationFilters()

    await storage.save_recommendations(run_id, recs)
    retrieved = await storage.get_recommendations(run_id, empty_filters)

    assert len(retrieved) == len(recs)


@pytest.mark.parametrize("make_storage", STORAGE_FACTORIES)
@given(data=st.data())
@settings(max_examples=100)
async def test_filter_subset_property(make_storage, data):
    """Filtered results are always a subset of unfiltered results."""
    storage = make_storage()
    run_id = data.draw(_id_st)
    recs = data.draw(st.lists(_recommendation_st(), min_size=0, max_size=10))
    filters = data.draw(_filters_st())

    await storage.save_recommendations(run_id, recs)
    all_recs = await storage.get_recommendations(run_id, None)
    filtered = await storage.get_recommendations(run_id, filters)

    assert len(filtered) <= len(all_recs)
