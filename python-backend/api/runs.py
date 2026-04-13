"""Runs API — POST /api/quality-evaluation/runs, GET /api/quality-evaluation/runs,
GET /api/quality-evaluation/runs/{runId}.

Port of app/api/quality-evaluation/runs/route.ts and runs/[runId]/route.ts.
"""

from __future__ import annotations

import math
import random
import time
from datetime import datetime, timezone

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from models.domain import AnalysisRun, RunSummaryMetrics
from models.requests import CreateRunRequest, CreateRunResponse, RunDetailResponse, ValidationSummary
from storage import get_storage

router = APIRouter()


def _generate_run_id() -> str:
    ts = int(time.time() * 1000)
    rand = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=7))
    return f"run-{ts}-{rand}"


@router.post("/api/quality-evaluation/runs", status_code=201)
async def create_run(body: CreateRunRequest) -> JSONResponse:
    storage = get_storage()

    run_id = _generate_run_id()
    now = datetime.now(timezone.utc).isoformat()

    # Look up the real-input import to get the record count
    real_input_import = await storage.get_import(body.real_input_dataset_id)
    total_real_inputs = real_input_import.record_count if real_input_import else 0

    run = AnalysisRun(
        id=run_id,
        createdAt=now,
        createdBy="system",
        updatedAt=now,
        version=1,
        runId=run_id,
        name=body.name,
        status="created",
        observationWindow=body.observation_window,
        realInputDatasetId=body.real_input_dataset_id,
        accuracyGoldenSetId=body.accuracy_golden_set_id,
        consistencyGoldenSetId=body.consistency_golden_set_id,
        referenceCatalogIds=body.reference_catalog_ids or [],
        materialityThreshold=body.materiality_threshold if body.materiality_threshold is not None else 0.01,
        minSampleSize=body.min_sample_size if body.min_sample_size is not None else 1000,
        confidenceLevel=body.confidence_level if body.confidence_level is not None else 0.95,
        protectedCaseRules=body.protected_case_rules or [],
        totalRealInputs=total_real_inputs,
        canonicalIntentCount=0,
        recommendationCount=0,
    )

    await storage.save_run(run)

    validation_summary = ValidationSummary(
        isValid=True,
        errors=[],
        warnings=[],
    )

    response = CreateRunResponse(
        runId=run_id,
        status=run.status,
        validationSummary=validation_summary,
    )

    return JSONResponse(
        status_code=201,
        content=response.model_dump(by_alias=True),
    )


@router.get("/api/quality-evaluation/runs")
async def list_runs() -> JSONResponse:
    storage = get_storage()
    runs = await storage.list_runs()
    return JSONResponse(
        status_code=200,
        content={"runs": [r.model_dump(by_alias=True) for r in runs]},
    )


@router.get("/api/quality-evaluation/runs/{run_id}")
async def get_run_detail(run_id: str) -> JSONResponse:
    storage = get_storage()

    run = await storage.get_run(run_id)
    if not run:
        return JSONResponse(status_code=404, content={"error": f"Run not found: {run_id}"})

    recommendations = await storage.get_recommendations(run_id)
    coverage_metrics = await storage.get_coverage_metrics(run_id)
    stability_metrics = await storage.get_stability_metrics(run_id)
    paraphrase_metrics = await storage.get_paraphrase_metrics(run_id)

    if coverage_metrics:
        cm_dicts = [m.model_dump(by_alias=True) for m in coverage_metrics]
        sm_dicts = [m.model_dump(by_alias=True) for m in stability_metrics]
        pm_dicts = [m.model_dump(by_alias=True) for m in paraphrase_metrics]
        rec_dicts = [r.model_dump(by_alias=True) for r in recommendations]

        summary_metrics = RunSummaryMetrics(
            observationWindow=run.observation_window,
            realInputsAnalyzed=run.total_real_inputs,
            canonicalIntentsFound=len(cm_dicts),
            accuracyIntentsCovered=len([m for m in cm_dicts if m.get("goldenSetCaseCount", 0) > 0 and m.get("realInputCount", 0) > 0]),
            consistencyGroupsReviewed=len(pm_dicts),
            realOnlyIntents=len([m for m in cm_dicts if m.get("classification") == "real-only"]),
            goldenOnlyIntents=len([m for m in cm_dicts if m.get("classification") == "golden-only"]),
            matchedIntents=len([m for m in cm_dicts if m.get("classification") == "matched"]),
            underrepresentedIntents=len([m for m in cm_dicts if m.get("classification") == "underrepresented"]),
            overrepresentedIntents=len([m for m in cm_dicts if m.get("classification") == "overrepresented"]),
            candidateObsoleteIntents=len([m for m in cm_dicts if m.get("classification") == "candidate-obsolete"]),
            actionReadyIntents=len([s for s in sm_dicts if s.get("actionability") == "action-ready"]),
            monitorIntents=len([s for s in sm_dicts if s.get("actionability") == "monitor"]),
            insufficientEvidenceIntents=len([s for s in sm_dicts if s.get("actionability") == "insufficient-evidence"]),
            narrowParaphraseGroups=len([p for p in pm_dicts if p.get("classification") == "narrow"]),
            criticalRecommendations=len([r for r in rec_dicts if r.get("priority") == "critical"]),
            protectedCasesRetained=len([m for m in cm_dicts if m.get("classification") == "protected-retained"]),
            materialityThreshold=run.materiality_threshold,
            confidenceLevel=run.confidence_level,
            meetsMinSampleSize=run.total_real_inputs >= run.min_sample_size,
        )
    else:
        summary_metrics = RunSummaryMetrics(
            observationWindow=run.observation_window,
            realInputsAnalyzed=run.total_real_inputs,
            canonicalIntentsFound=0,
            accuracyIntentsCovered=0,
            consistencyGroupsReviewed=0,
            realOnlyIntents=0,
            goldenOnlyIntents=0,
            matchedIntents=0,
            underrepresentedIntents=0,
            overrepresentedIntents=0,
            candidateObsoleteIntents=0,
            actionReadyIntents=0,
            monitorIntents=0,
            insufficientEvidenceIntents=0,
            narrowParaphraseGroups=0,
            criticalRecommendations=0,
            protectedCasesRetained=0,
            materialityThreshold=run.materiality_threshold,
            confidenceLevel=run.confidence_level,
            meetsMinSampleSize=run.total_real_inputs >= run.min_sample_size,
        )

    response = RunDetailResponse(
        run=run,
        summaryMetrics=summary_metrics,
        recommendations=recommendations,
    )

    return JSONResponse(
        status_code=200,
        content=response.model_dump(by_alias=True),
    )
