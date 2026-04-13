"""Property 20: BA/QA Approval Gate for Protected Recommendations

For any protected-class recommendation transitioning to 'approved' status,
the system should require a prior BA/QA approval decision. Without it,
the endpoint should return HTTP 403.

**Validates: Requirements 9.2**
"""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from httpx import AsyncClient, ASGITransport

from main import app
from storage import get_storage
from storage.memory import InMemoryStorage
import storage as storage_mod


# ─── Helpers ─────────────────────────────────────────────────────────────────

async def _setup_protected_recommendation(
    status: str = "po-review-pending",
    is_protected: bool = True,
) -> tuple[str, str]:
    """Create a run and protected recommendation, return (run_id, rec_id)."""
    store = get_storage()
    from models.domain import AnalysisRun, Recommendation

    run_id = f"run-baqa-{id(status)}"
    rec_id = f"rec-baqa-{id(status)}"
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
        isProtected=is_protected, protectedClasses=["policy-blocked"],
        actionability="protected-override", supportingRecordIds=[],
        supportingClusterIds=[],
    )
    await store.save_recommendations(run_id, [rec])
    return run_id, rec_id


# ─── Property Tests ─────────────────────────────────────────────────────────
# Feature: python-analysis-backend, Property 20: BA/QA Approval Gate for Protected Recommendations


@given(
    approver_role=st.sampled_from(["analyst", "po"]),
)
@settings(max_examples=100)
@pytest.mark.asyncio
async def test_protected_recommendation_requires_baqa_approval(approver_role: str):
    """A protected recommendation going to 'approved' without prior BA/QA approval returns 403."""
    storage_mod._instance = InMemoryStorage()

    # po-review-pending → approve → approved (the transition that triggers the gate)
    _, rec_id = await _setup_protected_recommendation(
        status="po-review-pending", is_protected=True,
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/quality-evaluation/approvals",
            json={
                "recommendationId": rec_id,
                "action": "approve",
                "reason": "test approval",
                "approverRole": approver_role,
            },
        )

    # Non-ba_qa roles should get 403 when no prior BA/QA approval exists
    assert resp.status_code == 403, (
        f"Expected 403 for {approver_role} approving protected rec, got {resp.status_code}"
    )
    body = resp.json()
    assert body.get("requiresBaQaApproval") is True


@given(data=st.data())
@settings(max_examples=100)
@pytest.mark.asyncio
async def test_baqa_role_can_approve_protected_recommendation(data: st.DataObject):
    """A BA/QA approver can approve a protected recommendation directly."""
    storage_mod._instance = InMemoryStorage()

    _, rec_id = await _setup_protected_recommendation(
        status="po-review-pending", is_protected=True,
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/quality-evaluation/approvals",
            json={
                "recommendationId": rec_id,
                "action": "approve",
                "reason": "BA/QA approved",
                "approverRole": "ba_qa",
            },
        )

    assert resp.status_code == 200, (
        f"Expected 200 for ba_qa approving protected rec, got {resp.status_code}: {resp.json()}"
    )
    body = resp.json()
    assert body["recommendation"]["status"] == "approved"


@given(
    approver_role=st.sampled_from(["analyst", "po"]),
)
@settings(max_examples=100)
@pytest.mark.asyncio
async def test_non_protected_recommendation_no_baqa_gate(approver_role: str):
    """A non-protected recommendation going to 'approved' does NOT require BA/QA approval."""
    storage_mod._instance = InMemoryStorage()

    _, rec_id = await _setup_protected_recommendation(
        status="po-review-pending", is_protected=False,
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/quality-evaluation/approvals",
            json={
                "recommendationId": rec_id,
                "action": "approve",
                "reason": "test",
                "approverRole": approver_role,
            },
        )

    # Non-protected recs should succeed without BA/QA gate
    assert resp.status_code == 200, (
        f"Expected 200 for {approver_role} approving non-protected rec, got {resp.status_code}"
    )
