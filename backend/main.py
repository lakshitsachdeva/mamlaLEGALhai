"""FastAPI application for RegulaTrace Phase 1."""

from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.engine import ENGINE_VERSION, analyze_document, compare_policy, compare_versions
from backend.schemas import (
    AnalyzeRequest,
    AnalysisResponse,
    CompareRequest,
    ComparisonResponse,
    ErrorResponse,
    HealthResponse,
    VersionCompareRequest,
    VersionCompareResponse,
)


def _cors_origins() -> list[str]:
    configured = os.getenv("REGULATRACE_CORS_ORIGINS")
    if configured:
        return [origin.strip() for origin in configured.split(",") if origin.strip()]
    return ["http://127.0.0.1:4173", "http://localhost:4173"]


app = FastAPI(
    title="RegulaTrace Deterministic Analysis API",
    description=(
        "Phase 1 backend for evidence-linked regulatory obligation extraction, "
        "policy comparison, and version change analysis. This API preserves the "
        "transparent JavaScript baseline semantics and is not legal advice."
    ),
    version="1.0.0-phase1",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Accept"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({"error": {"code": "VALIDATION_ERROR", "message": "The request payload is invalid.", "details": exc.errors()}}),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_request: Request, _exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_ERROR", "message": "RegulaTrace could not complete the deterministic analysis.", "details": None}},
    )


ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    422: {"model": ErrorResponse, "description": "Invalid input"},
    500: {"model": ErrorResponse, "description": "Unexpected analysis failure"},
}


@app.get("/api/health", response_model=HealthResponse, tags=["System"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "regulatrace-api", "phase": "phase-1-deterministic", "engineVersion": ENGINE_VERSION}


@app.post("/api/analyze", response_model=AnalysisResponse, responses=ERROR_RESPONSES, tags=["Analysis"])
def analyze(request: AnalyzeRequest) -> dict[str, Any]:
    metadata = request.source_metadata.model_dump(by_alias=True, exclude_none=True)
    return analyze_document(request.text, metadata)


@app.post("/api/compare", response_model=ComparisonResponse, responses=ERROR_RESPONSES, tags=["Analysis"])
def compare(request: CompareRequest) -> dict[str, Any]:
    return compare_policy(request.regulatory_text, request.policy_text)


@app.post("/api/versions/compare", response_model=VersionCompareResponse, responses=ERROR_RESPONSES, tags=["Analysis"])
def versions_compare(request: VersionCompareRequest) -> dict[str, Any]:
    return compare_versions(request.old_text, request.new_text)

