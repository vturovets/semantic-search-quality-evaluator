"""Exports API — POST /api/quality-evaluation/exports.

Port of app/api/quality-evaluation/exports/route.ts.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from engine.export import export_csv, export_json, export_markdown
from models.domain import ExportArtifact, RunSummaryMetrics
from models.requests import ExportRequest, ExportResponse
from storage import get_storage

router = APIRouter()


async def _gather_artifact_data(
    run_id: str,
    artifact_type: str,
    recommendations: list,
) -> list:
    """Gather data for a specific artifact type from storage."""
    storage = get_storage()

    if artifact_type == "run-summary":
        run = await storage.get_run(run_id)
        return [run.model_dump(by_alias=True)] if run else []
    elif artifact_type == "recommendation-list":
        return [r.model_dump(by_alias=True) for r in recommendations]
    elif artifact_type == "intent-coverage-table":
        metrics = await storage.get_coverage_metrics(run_id)
        return [m.model_dump(by_alias=True) for m in metrics]
    elif artifact_type == "wording-gap-table":
        metrics = await storage.get_paraphrase_metrics(run_id)
        return [m.model_dump(by_alias=True) for m in metrics]
    elif artifact_type == "approval-register":
        decisions = []
        for rec in recommendations:
            decs = await storage.get_decisions(rec.recommendation_id)
            decisions.extend([d.model_dump(by_alias=True) for d in decs])
        return decisions
    elif artifact_type == "change-proposal":
        return [
            r.model_dump(by_alias=True)
            for r in recommendations
            if r.status in ("approved", "implemented")
        ]
    return []


@router.post("/api/quality-evaluation/exports")
async def create_export(body: ExportRequest) -> JSONResponse:
    storage = get_storage()

    run = await storage.get_run(body.run_id)
    if not run:
        return JSONResponse(status_code=404, content={"error": f"Run not found: {body.run_id}"})

    recommendations = await storage.get_recommendations(body.run_id)

    # Generate export content for each requested artifact
    export_parts: list[str] = []
    for artifact_type in body.artifacts:
        data = await _gather_artifact_data(body.run_id, artifact_type, recommendations)

        if body.format == "markdown":
            if artifact_type == "run-summary":
                # Build summary metrics from stored analysis results
                coverage_metrics = await storage.get_coverage_metrics(body.run_id)
                stability_metrics = await storage.get_stability_metrics(body.run_id)
                paraphrase_metrics = await storage.get_paraphrase_metrics(body.run_id)

                cm_dicts = [m.model_dump(by_alias=True) for m in coverage_metrics]
                sm_dicts = [m.model_dump(by_alias=True) for m in stability_metrics]
                pm_dicts = [m.model_dump(by_alias=True) for m in paraphrase_metrics]
                rec_dicts = [r.model_dump(by_alias=True) for r in recommendations]

                summary_metrics = {
                    "observationWindow": run.observation_window,
                    "realInputsAnalyzed": run.total_real_inputs,
                    "canonicalIntentsFound": len(cm_dicts),
                    "accuracyIntentsCovered": len([m for m in cm_dicts if m.get("goldenSetCaseCount", 0) > 0 and m.get("realInputCount", 0) > 0]),
                    "consistencyGroupsReviewed": len(pm_dicts),
                    "realOnlyIntents": len([m for m in cm_dicts if m.get("classification") == "real-only"]),
                    "goldenOnlyIntents": len([m for m in cm_dicts if m.get("classification") == "golden-only"]),
                    "matchedIntents": len([m for m in cm_dicts if m.get("classification") == "matched"]),
                    "underrepresentedIntents": len([m for m in cm_dicts if m.get("classification") == "underrepresented"]),
                    "overrepresentedIntents": len([m for m in cm_dicts if m.get("classification") == "overrepresented"]),
                    "candidateObsoleteIntents": len([m for m in cm_dicts if m.get("classification") == "candidate-obsolete"]),
                    "actionReadyIntents": len([s for s in sm_dicts if s.get("actionability") == "action-ready"]),
                    "monitorIntents": len([s for s in sm_dicts if s.get("actionability") == "monitor"]),
                    "insufficientEvidenceIntents": len([s for s in sm_dicts if s.get("actionability") == "insufficient-evidence"]),
                    "narrowParaphraseGroups": len([p for p in pm_dicts if p.get("classification") == "narrow"]),
                    "criticalRecommendations": len([r for r in rec_dicts if r.get("priority") == "critical"]),
                    "protectedCasesRetained": len([m for m in cm_dicts if m.get("classification") == "protected-retained"]),
                    "materialityThreshold": run.materiality_threshold,
                    "confidenceLevel": run.confidence_level,
                    "meetsMinSampleSize": run.total_real_inputs >= run.min_sample_size,
                }

                export_parts.append(
                    export_markdown(run.model_dump(by_alias=True), summary_metrics, rec_dicts)
                )
            else:
                export_parts.append(export_json(data, artifact_type))
        elif body.format == "csv":
            export_parts.append(export_csv(data, artifact_type))
        elif body.format == "json":
            export_parts.append(export_json(data, artifact_type))

    # Persist the export artifact
    now = datetime.now(timezone.utc).isoformat()
    export_id = f"export-{int(time.time() * 1000)}"

    artifact = ExportArtifact(
        id=export_id,
        createdAt=now,
        createdBy="system",
        updatedAt=now,
        version=1,
        exportId=export_id,
        runId=body.run_id,
        format=body.format,
        artifacts=body.artifacts,
        generatedAt=now,
        piiSafe=True,
    )

    await storage.save_export_artifact(artifact)

    response = ExportResponse(
        exportId=export_id,
        downloadUrl=f"/api/quality-evaluation/exports/{export_id}/download",
        format=body.format,
    )

    return JSONResponse(
        status_code=200,
        content=response.model_dump(by_alias=True),
    )
