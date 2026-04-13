"""Property 5 (API-level): Record Validation Rejects Invalid Records at API Endpoints

For any API endpoint that accepts structured input, missing required fields
should result in a 400-level error response with validation details.

This extends the engine-level Property 5 test to cover API-level validation
via Pydantic request models.

**Validates: Requirements 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7**
"""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from httpx import AsyncClient, ASGITransport

from main import app
from storage.memory import InMemoryStorage
import storage as storage_mod


# ─── Strategies ──────────────────────────────────────────────────────────────

_nonempty_str = st.text(
    alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyz0123456789"),
    min_size=1,
    max_size=20,
)

CREATE_RUN_REQUIRED_FIELDS = [
    "name", "observationWindow", "realInputDatasetId",
]


def _valid_create_run_body():
    return {
        "name": "test-run",
        "observationWindow": 30,
        "realInputDatasetId": "ds-real",
        "accuracyGoldenSetId": "ds-acc",
        "consistencyGoldenSetId": "ds-con",
    }


NORMALIZE_REQUIRED_FIELDS = ["runId"]
ANALYZE_REQUIRED_FIELDS = ["runId"]

APPROVAL_REQUIRED_FIELDS = ["recommendationId", "action", "approverRole"]

EXPORT_REQUIRED_FIELDS = ["runId", "format", "artifacts"]


# ─── Property Tests ─────────────────────────────────────────────────────────
# Feature: python-analysis-backend, Property 5: Record Validation Rejects Invalid Records (API endpoints)


@given(field_to_remove=st.sampled_from(CREATE_RUN_REQUIRED_FIELDS))
@settings(max_examples=100)
@pytest.mark.asyncio
async def test_create_run_missing_required_field(field_to_remove: str):
    """POST /api/quality-evaluation/runs rejects requests missing required fields."""
    storage_mod._instance = InMemoryStorage()

    body = _valid_create_run_body()
    del body[field_to_remove]

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/quality-evaluation/runs", json=body)

    assert resp.status_code in (400, 422), (
        f"Expected 400/422 when missing '{field_to_remove}', got {resp.status_code}"
    )


@given(field_to_remove=st.sampled_from(APPROVAL_REQUIRED_FIELDS))
@settings(max_examples=100)
@pytest.mark.asyncio
async def test_approval_missing_required_field(field_to_remove: str):
    """POST /api/quality-evaluation/approvals rejects requests missing required fields."""
    storage_mod._instance = InMemoryStorage()

    body = {
        "recommendationId": "rec-1",
        "action": "approve",
        "approverRole": "analyst",
    }
    del body[field_to_remove]

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/quality-evaluation/approvals", json=body)

    assert resp.status_code in (400, 422), (
        f"Expected 400/422 when missing '{field_to_remove}', got {resp.status_code}"
    )


@given(field_to_remove=st.sampled_from(EXPORT_REQUIRED_FIELDS))
@settings(max_examples=100)
@pytest.mark.asyncio
async def test_export_missing_required_field(field_to_remove: str):
    """POST /api/quality-evaluation/exports rejects requests missing required fields."""
    storage_mod._instance = InMemoryStorage()

    body = {
        "runId": "run-1",
        "format": "json",
        "artifacts": ["run-summary"],
    }
    del body[field_to_remove]

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/quality-evaluation/exports", json=body)

    assert resp.status_code in (400, 422), (
        f"Expected 400/422 when missing '{field_to_remove}', got {resp.status_code}"
    )


@pytest.mark.asyncio
async def test_normalize_missing_run_id():
    """POST /api/quality-evaluation/normalize rejects requests without runId."""
    storage_mod._instance = InMemoryStorage()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/quality-evaluation/normalize", json={})

    assert resp.status_code in (400, 422)


@pytest.mark.asyncio
async def test_analyze_missing_run_id():
    """POST /api/quality-evaluation/analyze rejects requests without runId."""
    storage_mod._instance = InMemoryStorage()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/quality-evaluation/analyze", json={})

    assert resp.status_code in (400, 422)


@pytest.mark.asyncio
async def test_create_run_invalid_observation_window():
    """POST /api/quality-evaluation/runs rejects invalid observationWindow values."""
    storage_mod._instance = InMemoryStorage()

    body = _valid_create_run_body()
    body["observationWindow"] = 15  # Not 7, 30, or 90

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/quality-evaluation/runs", json=body)

    assert resp.status_code in (400, 422)
