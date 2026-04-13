"""Custom exception classes and FastAPI exception handlers.

Matches the same JSON error response shapes as the TypeScript routes.
"""

from __future__ import annotations

import json

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


# ─── Custom Exceptions ──────────────────────────────────────────────────────


class NotFoundError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ConflictError(Exception):
    def __init__(self, message: str, *, current_status: str | None = None, valid_transitions: list[str] | None = None):
        self.message = message
        self.current_status = current_status
        self.valid_transitions = valid_transitions
        super().__init__(message)


class ForbiddenError(Exception):
    def __init__(self, message: str, *, requires_ba_qa_approval: bool = False):
        self.message = message
        self.requires_ba_qa_approval = requires_ba_qa_approval
        super().__init__(message)


# ─── Exception Handlers ─────────────────────────────────────────────────────


def register_exception_handlers(app: FastAPI) -> None:
    """Register all custom exception handlers on the FastAPI app."""

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
        details = [str(e) for e in exc.errors()]
        return JSONResponse(
            status_code=400,
            content={"error": "Validation failed", "details": details},
        )

    @app.exception_handler(json.JSONDecodeError)
    async def json_decode_error_handler(_request: Request, _exc: json.JSONDecodeError) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid JSON in request body"},
        )

    @app.exception_handler(NotFoundError)
    async def not_found_handler(_request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"error": exc.message},
        )

    @app.exception_handler(ConflictError)
    async def conflict_handler(_request: Request, exc: ConflictError) -> JSONResponse:
        body: dict = {"error": exc.message}
        if exc.current_status is not None:
            body["currentStatus"] = exc.current_status
        if exc.valid_transitions is not None:
            body["validTransitions"] = exc.valid_transitions
        return JSONResponse(status_code=409, content=body)

    @app.exception_handler(ForbiddenError)
    async def forbidden_handler(_request: Request, exc: ForbiddenError) -> JSONResponse:
        body: dict = {"error": exc.message}
        if exc.requires_ba_qa_approval:
            body["requiresBaQaApproval"] = True
        return JSONResponse(status_code=403, content=body)

    @app.exception_handler(Exception)
    async def generic_error_handler(_request: Request, _exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"},
        )
