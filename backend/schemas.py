"""Typed API contracts for the RegulaTrace deterministic backend."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class APIModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class SourceMetadata(APIModel):
    source_id: str | None = Field(default=None, alias="sourceId")
    version: str | None = None
    authority: str | None = None
    jurisdiction: str | None = None
    section: str | None = None
    title: str | None = None


class AnalyzeRequest(APIModel):
    text: str = Field(min_length=1, max_length=250_000)
    source_metadata: SourceMetadata = Field(default_factory=SourceMetadata, alias="sourceMetadata")
    persist: bool = False

    @field_validator("text")
    @classmethod
    def text_must_contain_content(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("text must contain non-whitespace content")
        return value


class CompareRequest(APIModel):
    regulatory_text: str = Field(alias="regulatoryText", min_length=1, max_length=250_000)
    policy_text: str = Field(alias="policyText", min_length=1, max_length=250_000)

    @field_validator("regulatory_text", "policy_text")
    @classmethod
    def texts_must_contain_content(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("comparison text must contain non-whitespace content")
        return value


class VersionCompareRequest(APIModel):
    old_text: str = Field(alias="oldText", min_length=1, max_length=250_000)
    new_text: str = Field(alias="newText", min_length=1, max_length=250_000)

    @field_validator("old_text", "new_text")
    @classmethod
    def versions_must_contain_content(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("version text must contain non-whitespace content")
        return value


Modality = Literal["PROHIBITION", "OBLIGATION", "RECOMMENDATION", "PERMISSION", "INFORMATION"]


class SourceSpan(APIModel):
    start: int = Field(ge=0)
    end: int = Field(ge=0)


class FormalRule(APIModel):
    id: str = Field(min_length=1, max_length=80)
    source_id: str = Field(alias="sourceId", min_length=1, max_length=500)
    source_text: str = Field(alias="sourceText", min_length=1, max_length=20_000)
    evidence: str = Field(min_length=1, max_length=10_000)
    source_span: SourceSpan = Field(alias="sourceSpan")
    actor: str = Field(min_length=1, max_length=300)
    action: str = Field(min_length=1, max_length=300)
    object: str = Field(min_length=1, max_length=300)
    scope: str = Field(min_length=1, max_length=300)
    jurisdiction: str = Field(min_length=1, max_length=120)
    condition: str = Field(min_length=1, max_length=300)
    exception: str = Field(min_length=1, max_length=300)
    valid_from: str = Field(alias="validFrom")
    valid_until: str = Field(alias="validUntil")
    modality: Literal["OBLIGATION", "PROHIBITION", "PERMISSION"]

    @model_validator(mode="after")
    def validate_grounding(self) -> "FormalRule":
        span = self.source_span
        if span.end <= span.start or self.source_text[span.start:span.end] != self.evidence:
            raise ValueError("sourceSpan must recover evidence exactly from sourceText")
        for name in ("actor", "action", "object", "scope", "jurisdiction", "condition", "exception"):
            if not getattr(self, name).strip():
                raise ValueError(f"{name} must contain non-whitespace content")
        from datetime import date
        import re
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", self.valid_from) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", self.valid_until):
            raise ValueError("validFrom and validUntil must be ISO dates (YYYY-MM-DD)")
        try:
            start = date.fromisoformat(self.valid_from)
            end = date.fromisoformat(self.valid_until)
        except ValueError as exc:
            raise ValueError("validFrom and validUntil must be ISO dates (YYYY-MM-DD)") from exc
        if start > end:
            raise ValueError("validFrom must be on or before validUntil")
        return self


class ContradictionRequest(APIModel):
    left: FormalRule
    right: FormalRule

    @model_validator(mode="after")
    def distinct_ids(self) -> "ContradictionRequest":
        if self.left.id == self.right.id:
            raise ValueError("rule IDs must be distinct")
        return self


class ContradictionResponse(APIModel):
    verdict: Literal["INFEASIBLE_TO_SATISFY", "SATISFIABLE_UNDER_ENCODING", "NOT_COMPARABLE", "REVIEW_REQUIRED"]
    solver_status: Literal["unsat", "sat", "not_run", "unknown"] = Field(alias="solverStatus")
    explanation: str
    shared_interval: dict[str, str] | None = Field(alias="sharedInterval")
    alignment: dict[str, bool]
    proof_core: list[str] = Field(alias="proofCore")
    witness: dict[str, bool] | None
    assumptions: list[str]


class NeuroSymbolicRequest(ContradictionRequest):
    review_confirmed: Literal[True] = Field(alias="reviewConfirmed")


class NeuralSignal(APIModel):
    model_id: str = Field(alias="modelId")
    model_revision: str = Field(alias="modelRevision")
    cosine_similarity: float = Field(alias="cosineSimilarity", ge=-1, le=1)
    method: str
    truncated: dict[str, bool]
    note: str


class NeuroSymbolicResponse(APIModel):
    neural: NeuralSignal
    symbolic: ContradictionResponse


class ObligationRecord(APIModel):
    id: str
    source_id: str = Field(alias="sourceId")
    source_version: str = Field(alias="sourceVersion")
    authority: str
    jurisdiction: str
    section: str
    modality: Modality
    modality_cue: str = Field(alias="modalityCue")
    modality_confidence: float = Field(alias="modalityConfidence")
    actor: str
    action: str
    deadline: str | None
    condition: str | None
    exception: str | None
    cross_references: list[str] = Field(alias="crossReferences")
    evidence: str
    source_span: SourceSpan | None = Field(default=None, alias="sourceSpan")
    review_state: str = Field(alias="reviewState")
    severity: Literal["HIGH", "MEDIUM", "STANDARD"]
    unresolved: list[str]
    confidence: float


class AnalysisSummary(APIModel):
    clause_count: int = Field(alias="clauseCount")
    obligation_count: int = Field(alias="obligationCount")
    unresolved_count: int = Field(alias="unresolvedCount")
    avg_confidence: float = Field(alias="avgConfidence")
    citation_integrity: float = Field(alias="citationIntegrity")
    modality_counts: dict[str, int] = Field(alias="modalityCounts")


class AnalysisResponse(APIModel):
    analysis_id: str | None = Field(default=None, alias="analysisId")
    engine_version: str = Field(alias="engineVersion")
    analyzed_at: str = Field(alias="analyzedAt")
    source: SourceMetadata
    records: list[ObligationRecord]
    normative: list[ObligationRecord]
    summary: AnalysisSummary


class ComparisonDimension(APIModel):
    id: str
    label: str
    score: float
    detail: str


class ComparisonResponse(APIModel):
    requirement: ObligationRecord | None
    policy: ObligationRecord | None
    dimensions: list[ComparisonDimension]
    score: float
    outcome: Literal["POTENTIAL_MISMATCH", "LIKELY_ALIGNED", "REVIEW_REQUIRED"]
    lexical_similarity: float = Field(alias="lexicalSimilarity")


class ChangeExplanation(APIModel):
    observed: str
    possible_rationale: str = Field(alias="possibleRationale")
    operational_impact: str = Field(alias="operationalImpact")
    status: Literal["INFERRED_FROM_TEXT", "UNDETERMINED"]


class VersionChange(APIModel):
    id: str
    type: Literal["MODIFIED", "ADDED", "REMOVED"]
    before: str | None
    after: str | None
    similarity: float
    severity: Literal["CRITICAL", "MATERIAL"]
    explanation: ChangeExplanation


class VersionCompareResponse(APIModel):
    changes: list[VersionChange]
    counts: dict[str, int]
    affected_obligations: int = Field(alias="affectedObligations")
    critical_count: int = Field(alias="criticalCount")
    materiality_score: int = Field(alias="materialityScore")


class HealthResponse(APIModel):
    status: Literal["ok"]
    service: str
    phase: str
    engine_version: str = Field(alias="engineVersion")


class IngestResponse(APIModel):
    filename: str
    format: str
    text: str
    characters: int
    words: int
    pages: int


class ReviewRequest(APIModel):
    analysis_id: str = Field(alias="analysisId", min_length=3, max_length=64)
    record_id: str = Field(alias="recordId", min_length=3, max_length=128)
    decision: Literal["CONFIRMED", "CORRECTED", "REJECTED"]
    note: str | None = Field(default=None, max_length=2_000)
    reviewer: str = Field(default="Presentation reviewer", min_length=2, max_length=120)
    corrected_fields: dict[Literal["actor", "action", "modality", "deadline", "condition", "exception"], str | None] = Field(default_factory=dict, alias="correctedFields")

    @model_validator(mode="after")
    def correction_must_change_fields(self) -> "ReviewRequest":
        if self.decision == "CORRECTED" and not self.corrected_fields:
            raise ValueError("a corrected review must supply correctedFields")
        if self.decision != "CORRECTED" and self.corrected_fields:
            raise ValueError("correctedFields are only accepted for a corrected review")
        for field, value in self.corrected_fields.items():
            if field in {"actor", "action", "modality"} and (value is None or not value.strip()):
                raise ValueError(f"{field} cannot be empty")
            if value is not None and len(value) > 2_000:
                raise ValueError(f"{field} is too long")
        if "modality" in self.corrected_fields and self.corrected_fields["modality"] not in {"PROHIBITION", "OBLIGATION", "RECOMMENDATION", "PERMISSION", "INFORMATION"}:
            raise ValueError("modality is invalid")
        return self


class ReviewResponse(APIModel):
    analysis_id: str = Field(alias="analysisId")
    record_id: str = Field(alias="recordId")
    decision: str
    reviewer: str
    note: str | None
    created_at: str = Field(alias="createdAt")
    reviewed_count: int = Field(alias="reviewedCount")
    changes: dict[str, dict[str, str | None]] = Field(default_factory=dict)


class AnalysisHistoryItem(APIModel):
    analysis_id: str = Field(alias="analysisId")
    created_at: str = Field(alias="createdAt")
    source_title: str = Field(alias="sourceTitle")
    authority: str
    jurisdiction: str
    record_count: int = Field(alias="recordCount")
    unresolved_count: int = Field(alias="unresolvedCount")
    reviewed_count: int = Field(alias="reviewedCount")


class AuditEvent(APIModel):
    record_id: str = Field(alias="recordId")
    decision: str
    note: str | None
    reviewer: str
    created_at: str = Field(alias="createdAt")
    changes: dict[str, dict[str, str | None]] = Field(default_factory=dict)


class DashboardResponse(APIModel):
    analyses: int
    records: int
    unresolved: int
    reviewed: int
    decisions: dict[str, int]
    database: str


class BenchmarkResponse(APIModel):
    benchmark: str
    dataset_type: str = Field(alias="datasetType")
    executed_cases: int = Field(alias="executedCases")
    passed_cases: int = Field(alias="passedCases")
    pass_rate: float = Field(alias="passRate")
    metrics: dict[str, float]
    suites: dict[str, list[dict[str, Any]]]


class ErrorBody(APIModel):
    code: str
    message: str
    details: Any | None = None


class ErrorResponse(APIModel):
    error: ErrorBody

