"""Import API — POST /api/quality-evaluation/import (multipart form data).

Port of app/api/quality-evaluation/import/route.ts.
"""

from __future__ import annotations

import random
import time
from datetime import datetime, timezone

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse

from engine.parser import parse_csv, parse_json, parse_markdown_table
from models.domain import DatasetImport, ValidationIssue
from models.requests import ImportResponse
from storage import get_storage

router = APIRouter()

VALID_DATASET_TYPES = [
    "real-input",
    "accuracy-golden-set",
    "consistency-golden-set",
    "status-mapping",
    "reference-catalog",
]


def _detect_format(file_name: str) -> str | None:
    ext = file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ""
    if ext == "csv":
        return "csv"
    if ext == "json":
        return "json"
    if ext == "md":
        return "md"
    return None


def _generate_import_id() -> str:
    ts = int(time.time() * 1000)
    rand = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=7))
    return f"imp-{ts}-{rand}"


@router.post("/api/quality-evaluation/import", status_code=201)
async def import_dataset(
    file: UploadFile = File(...),
    datasetType: str = Form(...),
    name: str = Form(...),
    version: str | None = Form(default=None),
) -> JSONResponse:
    storage = get_storage()

    # Validate metadata
    if not name or not name.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid import metadata", "details": ["name is required and must be a non-empty string"]},
        )

    if datasetType not in VALID_DATASET_TYPES:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid import metadata", "details": [f"datasetType must be one of: {', '.join(VALID_DATASET_TYPES)}"]},
        )

    # Detect format from file extension
    file_name = file.filename or "unknown"
    fmt = _detect_format(file_name)
    if not fmt:
        return JSONResponse(
            status_code=400,
            content={"error": f"Unsupported file format: {file_name}. Supported formats: .csv, .json, .md"},
        )

    # Read file content
    content = (await file.read()).decode("utf-8")

    # Parse using the appropriate parser
    if fmt == "csv":
        parse_result = parse_csv(content, datasetType)
    elif fmt == "json":
        parse_result = parse_json(content, datasetType)
    else:
        parse_result = parse_markdown_table(content, datasetType)

    # Determine validation status
    has_errors = any(i.get("severity") == "error" for i in parse_result.issues)
    has_warnings = any(i.get("severity") == "warning" for i in parse_result.issues)
    validation_status: str = "rejected" if has_errors else ("warnings" if has_warnings else "valid")

    # Create and persist DatasetImport record
    import_id = _generate_import_id()
    now = datetime.now(timezone.utc).isoformat()

    validation_issues = [
        ValidationIssue(
            row=issue.get("row"),
            field=issue.get("field"),
            severity=issue.get("severity", "error"),
            message=issue.get("message", ""),
        )
        for issue in parse_result.issues
    ]

    dataset_import = DatasetImport(
        id=import_id,
        createdAt=now,
        createdBy="system",
        updatedAt=now,
        version=1,
        importId=import_id,
        datasetType=datasetType,
        fileName=file_name,
        recordCount=len(parse_result.records),
        validationStatus=validation_status,
        validationIssues=validation_issues,
        parsedAt=now,
    )

    await storage.save_import(dataset_import)

    # Persist the parsed records for later normalization/analysis
    if validation_status != "rejected":
        await storage.save_imported_records(import_id, parse_result.records)

    response = ImportResponse(
        importId=import_id,
        recordCount=len(parse_result.records),
        validationIssues=validation_issues,
        status=validation_status,
    )

    return JSONResponse(
        status_code=201,
        content=response.model_dump(by_alias=True),
    )
