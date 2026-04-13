"""Analyze API — POST /api/quality-evaluation/analyze.

Port of app/api/quality-evaluation/analyze/route.ts.
Full pipeline: normalize → compare → classify → evaluate stability → enrich → paraphrase → recommend → persist.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from engine.comparison import ComparisonConfig, compare_intent_coverage
from engine.consistency_metrics import analyze_paraphrase_groups
from engine.coverage_metrics import classify_intents, compute_coverage_metrics
from engine.normalization import normalize_dataset
from engine.recommendation_engine import RecommendationEngineConfig, generate_recommendations
from engine.statistical_evaluation import (
    IntentObservation,
    StabilityEvaluationConfig,
    evaluate_intent_stability,
)
from models.domain import (
    IntentCoverageMetric,
    IntentShareStabilityMetric,
    NormalizedRecord as NRModel,
    ParaphraseCoverageMetric,
    Recommendation as RecModel,
)
from models.requests import AnalyzeRequest, AnalyzeResponse
from storage import get_storage

router = APIRouter()


@router.post("/api/quality-evaluation/analyze")
async def analyze(body: AnalyzeRequest) -> JSONResponse:
    storage = get_storage()

    run = await storage.get_run(body.run_id)
    if not run:
        return JSONResponse(status_code=404, content={"error": f"Run not found: {body.run_id}"})

    run_id = body.run_id

    # Load or build normalized records for real inputs
    normalized_real_models = await storage.get_normalized_records(run_id)
    if not normalized_real_models:
        raw_real = await storage.get_imported_records(run.real_input_dataset_id)
        if not raw_real:
            return JSONResponse(
                status_code=400,
                content={"error": "No imported records found for the real-input dataset. Please upload data first."},
            )
        normalized_real_dicts = normalize_dataset(raw_real, "real-input")
        normalized_real_models = [NRModel.model_validate(d) for d in normalized_real_dicts]
        await storage.save_normalized_records(run_id, normalized_real_models)

    # Load or build normalized records for accuracy golden set
    normalized_accuracy_models = []
    if run.accuracy_golden_set_id:
        normalized_accuracy_models = await storage.get_normalized_records(f"{run_id}:accuracy")
        if not normalized_accuracy_models:
            raw_accuracy = await storage.get_imported_records(run.accuracy_golden_set_id)
            if raw_accuracy:
                accuracy_dicts = normalize_dataset(raw_accuracy, "accuracy-golden-set")
                normalized_accuracy_models = [NRModel.model_validate(d) for d in accuracy_dicts]
                await storage.save_normalized_records(f"{run_id}:accuracy", normalized_accuracy_models)

    # Load or build normalized records for consistency golden set
    normalized_consistency_models = []
    if run.consistency_golden_set_id:
        normalized_consistency_models = await storage.get_normalized_records(f"{run_id}:consistency")
        if not normalized_consistency_models:
            raw_consistency = await storage.get_imported_records(run.consistency_golden_set_id)
            if raw_consistency:
                consistency_dicts = normalize_dataset(raw_consistency, "consistency-golden-set")
                normalized_consistency_models = [NRModel.model_validate(d) for d in consistency_dicts]
                await storage.save_normalized_records(f"{run_id}:consistency", normalized_consistency_models)

    # Convert models to dicts for engine functions
    normalized_real = [r.model_dump(by_alias=True) for r in normalized_real_models]
    normalized_accuracy = [r.model_dump(by_alias=True) for r in normalized_accuracy_models]
    normalized_consistency = [r.model_dump(by_alias=True) for r in normalized_consistency_models]

    # Build protected intent IDs from run config
    protected_intent_ids: set[str] = set()
    for r in normalized_real:
        hint = (r.get("originalValues") or {}).get("protectedClassHint")
        if hint:
            protected_intent_ids.add(r["normalizedIntent"])
    for r in normalized_accuracy:
        pc = (r.get("originalValues") or {}).get("protectedClass")
        if pc:
            protected_intent_ids.add(r["normalizedIntent"])

    comparison_config = ComparisonConfig(
        run_id=run_id,
        materiality_threshold=run.materiality_threshold,
        min_sample_size=run.min_sample_size,
        confidence_level=run.confidence_level,
        protected_intent_ids=protected_intent_ids,
    )

    # 1. Comparison: intent coverage (only if accuracy golden set provided)
    if normalized_accuracy:
        raw_coverage_metrics = compare_intent_coverage(
            normalized_real, normalized_accuracy, comparison_config,
        )
    else:
        raw_coverage_metrics = []

    # 2. Coverage metrics: classify intents
    classified_coverage = classify_intents(
        raw_coverage_metrics, run.materiality_threshold, protected_intent_ids,
    )

    # 3. Statistical evaluation: stability metrics
    intent_observations = [
        IntentObservation(intent_id=m["intentId"], observed_count=m["realInputCount"])
        for m in classified_coverage
    ]
    total_sample = len(normalized_real)

    protected_intent_map: dict[str, bool] = {pid: True for pid in protected_intent_ids}

    stability_metrics = evaluate_intent_stability(
        intent_observations,
        total_sample,
        StabilityEvaluationConfig(
            run_id=run_id,
            confidence_level=run.confidence_level,
            materiality_threshold=run.materiality_threshold,
            min_sample_size=run.min_sample_size,
            protected_intents=protected_intent_map,
        ),
    )

    # Enrich coverage metrics with statistical CI and actionability
    enriched_coverage = []
    for metric in classified_coverage:
        stability = next((s for s in stability_metrics if s["intentId"] == metric["intentId"]), None)
        if stability:
            enriched = {
                **metric,
                "confidenceInterval": stability["confidenceInterval"],
                "actionability": stability["actionability"],
            }
        else:
            enriched = metric
        enriched_coverage.append(enriched)

    # 4. Consistency metrics: paraphrase group analysis (only if consistency golden set provided)
    if normalized_consistency:
        wording_metrics = analyze_paraphrase_groups(
            normalized_real, normalized_consistency, comparison_config,
        )
    else:
        wording_metrics = []

    # 5. Recommendation generation
    rec_config = RecommendationEngineConfig(
        run_id=run_id,
        materiality_threshold=run.materiality_threshold,
        protected_case_rules=[r.model_dump(by_alias=True) for r in run.protected_case_rules],
        observation_window=run.observation_window,
    )
    recommendations = generate_recommendations(
        enriched_coverage, stability_metrics, wording_metrics, rec_config,
    )

    # Persist all results — convert dicts to Pydantic models
    coverage_models = [IntentCoverageMetric.model_validate(m) for m in enriched_coverage]
    stability_models = [IntentShareStabilityMetric.model_validate(s) for s in stability_metrics]
    paraphrase_models = [ParaphraseCoverageMetric.model_validate(p) for p in wording_metrics]
    rec_models = [RecModel.model_validate(r) for r in recommendations]

    await storage.save_coverage_metrics(run_id, coverage_models)
    await storage.save_stability_metrics(run_id, stability_models)
    await storage.save_paraphrase_metrics(run_id, paraphrase_models)
    await storage.save_recommendations(run_id, rec_models)

    # Update run status and counts
    coverage_summary = compute_coverage_metrics(enriched_coverage)
    run.status = "completed"
    run.total_real_inputs = total_sample
    run.canonical_intent_count = coverage_summary.total
    run.recommendation_count = len(recommendations)
    run.completed_at = datetime.now(timezone.utc).isoformat()
    await storage.save_run(run)

    response = AnalyzeResponse(
        coverageMetrics=coverage_models,
        stabilityMetrics=stability_models,
        wordingMetrics=paraphrase_models,
        recommendationCount=len(recommendations),
        status=run.status,
    )

    return JSONResponse(
        status_code=200,
        content=response.model_dump(by_alias=True),
    )
