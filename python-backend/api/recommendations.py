"""Recommendations API — GET /api/quality-evaluation/recommendations (filtered, paginated),
PATCH /api/quality-evaluation/recommendations/{id}.

Port of app/api/quality-evaluation/recommendations/route.ts and [id]/route.ts.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from models.requests import RecommendationFilters, RecommendationListResponse, UpdateRecommendationRequest
from storage import get_storage

router = APIRouter()


@router.get("/api/quality-evaluation/recommendations")
async def list_recommendations(
    runId: str = Query(...),
    page: int = Query(default=1),
    pageSize: int = Query(default=20),
    type: Optional[str] = Query(default=None),
    priority: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    protectedFlag: Optional[str] = Query(default=None),
    intentFamily: Optional[str] = Query(default=None),
    goldenSet: Optional[str] = Query(default=None),
) -> JSONResponse:
    storage = get_storage()

    run = await storage.get_run(runId)
    if not run:
        return JSONResponse(status_code=404, content={"error": f"Run not found: {runId}"})

    page = max(1, page)
    pageSize = max(1, min(100, pageSize))

    filters = RecommendationFilters()
    if type:
        filters.type = type  # type: ignore[assignment]
    if priority:
        filters.priority = priority  # type: ignore[assignment]
    if status:
        filters.status = status  # type: ignore[assignment]
    if protectedFlag is not None:
        filters.protected_flag = protectedFlag == "true"
    if intentFamily:
        filters.intent_family = intentFamily
    if goldenSet:
        filters.golden_set = goldenSet  # type: ignore[assignment]

    all_filtered = await storage.get_recommendations(runId, filters)
    total = len(all_filtered)
    start = (page - 1) * pageSize
    items = all_filtered[start : start + pageSize]

    response = RecommendationListResponse(
        items=items,
        total=total,
        page=page,
        pageSize=pageSize,
    )

    return JSONResponse(
        status_code=200,
        content=response.model_dump(by_alias=True),
    )


@router.patch("/api/quality-evaluation/recommendations/{rec_id}")
async def update_recommendation(rec_id: str, body: UpdateRecommendationRequest) -> JSONResponse:
    storage = get_storage()

    # Find the recommendation across all runs
    runs = await storage.list_runs()
    found = None
    found_run_id = None

    for run in runs:
        recs = await storage.get_recommendations(run.run_id)
        match = next((r for r in recs if r.recommendation_id == rec_id), None)
        if match:
            found = match
            found_run_id = run.run_id
            break

    if not found or not found_run_id:
        return JSONResponse(
            status_code=404,
            content={"error": f"Recommendation not found: {rec_id}"},
        )

    update: dict = {}
    if body.priority is not None:
        update["priority"] = body.priority
    if body.rationale is not None:
        update["reason"] = body.rationale
    if body.status is not None:
        update["status"] = body.status
    if body.proposed_action is not None:
        update["proposed_action"] = body.proposed_action
    update["updated_at"] = datetime.now(timezone.utc).isoformat()

    await storage.update_recommendation(rec_id, update)

    # Fetch the updated recommendation
    updated_recs = await storage.get_recommendations(found_run_id)
    updated = next((r for r in updated_recs if r.recommendation_id == rec_id), None)

    return JSONResponse(
        status_code=200,
        content=updated.model_dump(by_alias=True) if updated else {},
    )
