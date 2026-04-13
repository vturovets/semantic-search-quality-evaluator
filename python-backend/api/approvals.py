"""Approvals API — POST /api/quality-evaluation/approvals.

Port of app/api/quality-evaluation/approvals/route.ts.
Implements resolveTargetStatus matching the TypeScript logic.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from models.domain import RecommendationDecision
from models.enums import VALID_TRANSITIONS, RecommendationStatus
from models.requests import ApprovalRequest
from storage import get_storage

router = APIRouter()


def resolve_target_status(
    current_status: str,
    action: str,
) -> str | None:
    """Determine the target status for an approval action based on the current status.

    'approve' advances to the next valid non-rejected state.
    'reject' moves to 'rejected' if that's a valid transition.
    """
    valid_targets = VALID_TRANSITIONS.get(current_status, [])
    if not valid_targets:
        return None

    if action == "reject":
        return "rejected" if "rejected" in valid_targets else None

    # 'approve' — pick the first valid non-rejected target
    advance_target = next((s for s in valid_targets if s != "rejected"), None)
    return advance_target


@router.post("/api/quality-evaluation/approvals")
async def create_approval(body: ApprovalRequest) -> JSONResponse:
    storage = get_storage()

    # Find the recommendation across all runs
    runs = await storage.list_runs()
    found = None
    found_run_id = None

    for run in runs:
        recs = await storage.get_recommendations(run.run_id)
        match = next((r for r in recs if r.recommendation_id == body.recommendation_id), None)
        if match:
            found = match
            found_run_id = run.run_id
            break

    if not found or not found_run_id:
        return JSONResponse(
            status_code=404,
            content={"error": f"Recommendation not found: {body.recommendation_id}"},
        )

    # Resolve target status from state machine
    target_status = resolve_target_status(found.status, body.action)
    if not target_status:
        return JSONResponse(
            status_code=409,
            content={
                "error": f"Invalid state transition: cannot {body.action} from '{found.status}'",
                "currentStatus": found.status,
                "validTransitions": VALID_TRANSITIONS.get(found.status, []),
            },
        )

    # Enforce BA/QA approval requirement for protected-class recommendations
    # going to 'approved' state
    if target_status == "approved" and found.is_protected:
        if body.approver_role != "ba_qa":
            existing_decisions = await storage.get_decisions(body.recommendation_id)
            has_ba_qa_approval = any(
                d.decided_by == "ba_qa" and d.to_status == "approved"
                for d in existing_decisions
            )
            if not has_ba_qa_approval:
                return JSONResponse(
                    status_code=403,
                    content={
                        "error": "Protected-class recommendation requires BA/QA approval before final approval",
                        "requiresBaQaApproval": True,
                    },
                )

    # Create the decision record
    now = datetime.now(timezone.utc).isoformat()
    decision = RecommendationDecision(
        id=f"decision-{int(time.time() * 1000)}",
        createdAt=now,
        createdBy=body.approver_role,
        updatedAt=now,
        version=1,
        recommendationId=body.recommendation_id,
        fromStatus=found.status,
        toStatus=target_status,
        action="advance" if body.action == "approve" else "reject",
        reason=body.reason,
        decidedBy=body.approver_role,
        decidedAt=now,
        requiresBaQaApproval=found.is_protected and target_status == "approved",
        baQaApproved=True if body.approver_role == "ba_qa" else None,
    )

    # Persist the decision
    await storage.save_decision(decision)

    # Update the recommendation status
    await storage.update_recommendation(body.recommendation_id, {
        "status": target_status,
        "updated_at": now,
    })

    # Fetch the updated recommendation
    updated_recs = await storage.get_recommendations(found_run_id)
    updated = next((r for r in updated_recs if r.recommendation_id == body.recommendation_id), None)

    return JSONResponse(
        status_code=200,
        content={
            "recommendation": updated.model_dump(by_alias=True) if updated else {},
            "decision": decision.model_dump(by_alias=True),
        },
    )
