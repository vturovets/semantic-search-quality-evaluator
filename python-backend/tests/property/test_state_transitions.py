"""Property 19: State Transition Enforcement

For any recommendation in a given status and for any target status,
the approval endpoint should allow the transition if and only if the target
is in the VALID_TRANSITIONS[currentStatus] list. Invalid transitions should
return HTTP 409.

**Validates: Requirements 9.1, 9.4**
"""

from __future__ import annotations

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from httpx import AsyncClient, ASGITransport

from main import app
from models.enums import VALID_TRANSITIONS, RecommendationStatus
from storage import get_storage
from storage.memory import InMemoryStorage
import storage as storage_mod

# All possible statuses
ALL_STATUSES = list(VALID_TRANSITIONS.keys())


# ─── Helpers ─────────────────────────────────────────────────────────────────

async def _setup_recommendation(status: str, is_protected: bool = False) -> tuple[str, str]:
    """Create a run and recommendation in the given status, return (run_id, rec_id)."""
    store = get_storage()
    from models.domain import AnalysisRun, Recommendation

    run_id = f"run-test-{id(status)}"
    rec_id = f"rec-test-{id(status)}"
    now = "2025-01-01T00:00:00Z"

    run = AnalysisRun(
        id=run_id, createdAt=now, createdBy="test", updatedAt=now, version=1,
        runId=run_id, name="test", status="completed", observationWindow=30,
        realInputDatasetId="ds1", accuracyGoldenSetId="ds2",
        consistencyGoldenSetId="ds3", referenceCatalogIds=[],
        materialityThreshold=0.01, minSampleSize=100, confidenceLevel=0.95,
        protectedCaseRules=[], totalRealInputs=1000,
        canonicalIntentCount=10, recommendationCount=1,
    )
    await store.save_run(run)

    rec = Recommendation(
        id=rec_id, createdAt=now, createdBy="test", updatedAt=now, version=1,
        recommendationId=rec_id, runId=run_id, type="add-new-intent",
        affectedGoldenSet="accuracy", impactedIntentId="intent-1",
        impactedIntentFamily="family-1", reason="test",
        observedFrequency=10, observedSharePercent=5.0,
        currentGoldenRepresentation=0, identifiedGap="gap",
        proposedAction="action", priority="high", status=status,
        isProtected=is_protected, protectedClasses=[],
        actionability="action-ready", supportingRecordIds=[],
        supportingClusterIds=[],
    )
    await store.save_recommendations(run_id, [rec])
    return run_id, rec_id


# ─── Property Tests ─────────────────────────────────────────────────────────
# Feature: python-analysis-backend, Property 19: State Transition Enforcement


@given(
    current_status=st.sampled_from(ALL_STATUSES),
    action=st.sampled_from(["approve", "reject"]),
)
@settings(max_examples=100)
@pytest.mark.asyncio
async def test_state_transition_enforcement(current_status: str, action: str):
    """Valid transitions succeed; invalid transitions return 409."""
    # Reset storage for each test
    storage_mod._instance = InMemoryStorage()

    run_id, rec_id = await _setup_recommendation(current_status, is_protected=False)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/quality-evaluation/approvals",
            json={
                "recommendationId": rec_id,
                "action": action,
                "reason": "test",
                "approverRole": "analyst",
            },
        )

    valid_targets = VALID_TRANSITIONS.get(current_status, [])

    if action == "reject":
        expected_target = "rejected" if "rejected" in valid_targets else None
    else:
        expected_target = next((s for s in valid_targets if s != "rejected"), None)

    if expected_target is None:
        # Should be 409 — invalid transition
        assert resp.status_code == 409, (
            f"Expected 409 for {action} from '{current_status}', got {resp.status_code}"
        )
        body = resp.json()
        assert "error" in body
        assert body.get("currentStatus") == current_status
    else:
        # Should be 200 — valid transition
        assert resp.status_code == 200, (
            f"Expected 200 for {action} from '{current_status}' → '{expected_target}', "
            f"got {resp.status_code}: {resp.json()}"
        )
