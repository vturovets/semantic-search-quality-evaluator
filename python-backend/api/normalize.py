"""Normalize API — POST /api/quality-evaluation/normalize.

Port of app/api/quality-evaluation/normalize/route.ts.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from engine.normalization import normalize_dataset
from models.requests import NormalizeRequest, NormalizeResponse
from storage import get_storage

router = APIRouter()


@router.post("/api/quality-evaluation/normalize")
async def normalize(body: NormalizeRequest) -> JSONResponse:
    storage = get_storage()

    run = await storage.get_run(body.run_id)
    if not run:
        return JSONResponse(
            status_code=404,
            content={"error": f"Run not found: {body.run_id}"},
        )

    # Load or build normalized records from raw imported data
    source_records = await storage.get_normalized_records(body.run_id)
    warnings: list[str] = []

    if not source_records:
        raw_records = await storage.get_imported_records(run.real_input_dataset_id)
        if not raw_records:
            return JSONResponse(
                status_code=400,
                content={"error": "No imported records found for this run. Please upload datasets first."},
            )
        normalized_dicts = normalize_dataset(raw_records, "real-input")
        # Convert dicts to NormalizedRecord models for storage
        from models.domain import NormalizedRecord as NRModel
        source_records = [NRModel.model_validate(d) for d in normalized_dicts]
        await storage.save_normalized_records(body.run_id, source_records)

    # Collect unique canonical intents
    canonical_intents = set(r.normalized_intent for r in source_records)

    response = NormalizeResponse(
        canonicalIntentCount=len(canonical_intents),
        normalizedRecordCount=len(source_records),
        warnings=warnings,
    )

    return JSONResponse(
        status_code=200,
        content=response.model_dump(by_alias=True),
    )
