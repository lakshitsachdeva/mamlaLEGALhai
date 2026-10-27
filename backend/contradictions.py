"""Conditional compliance-feasibility proof for two reviewer-normalized rules."""

from __future__ import annotations

from datetime import date

from z3 import Bool, Not, Solver, sat, unsat

from backend.schemas import ContradictionRequest


def _key(value: str) -> str:
    """Only case and whitespace are normalized; synonyms require human review."""
    return " ".join(value.casefold().split())


def check_contradiction(request: ContradictionRequest) -> dict:
    left, right = request.left, request.right
    fields = ("actor", "action", "object", "scope", "jurisdiction", "condition")
    alignment = {field: _key(getattr(left, field)) == _key(getattr(right, field)) for field in fields}
    start = max(date.fromisoformat(left.valid_from), date.fromisoformat(right.valid_from))
    end = min(date.fromisoformat(left.valid_until), date.fromisoformat(right.valid_until))
    overlap = start <= end
    alignment["time"] = overlap
    interval = {"start": start.isoformat(), "end": end.isoformat()} if overlap else None
    assumptions = [
        "The supplied source text and manual rule fields are accurate; source IDs are labels, not authority checks.",
        "Equal normalized actor, action, object, scope, jurisdiction, and condition denote the same act.",
        "Both rules apply throughout their stated inclusive date ranges; no priority or legal override is modeled.",
        "Obligation requires the act and prohibition forbids it at one instant in the shared interval.",
    ]
    base = {"sharedInterval": interval, "alignment": alignment, "proofCore": [], "witness": None, "assumptions": assumptions}
    if not overlap or not all(alignment.values()):
        return {**base, "verdict": "NOT_COMPARABLE", "solverStatus": "not_run",
                "explanation": "The rules do not have an identical reviewed act and overlapping period under this strict matcher. This does not establish legal compatibility."}
    if _key(left.exception) != "none" or _key(right.exception) != "none":
        return {**base, "verdict": "REVIEW_REQUIRED", "solverStatus": "not_run",
                "explanation": "An exception is present. Its applicability or precedence must be resolved before formal checking."}
    if "PERMISSION" in (left.modality, right.modality):
        return {**base, "verdict": "REVIEW_REQUIRED", "solverStatus": "not_run",
                "explanation": "Permission is not encoded as a required action; its interaction with these rules needs legal interpretation."}

    perform = Bool("perform_act_during_shared_interval")
    solver = Solver()
    solver.set(timeout=3000)
    tracking = {}
    for label, rule in (("left", left), ("right", right)):
        constraint = perform if rule.modality == "OBLIGATION" else Not(perform)
        marker = Bool(f"__track_{label}")
        tracking[str(marker)] = rule.id
        solver.assert_and_track(constraint, marker)
    result = solver.check()
    if result == unsat:
        core = {tracking[str(item)] for item in solver.unsat_core()}
        return {**base, "verdict": "INFEASIBLE_TO_SATISFY", "solverStatus": "unsat",
                "proofCore": [rule.id for rule in (left, right) if rule.id in core],
                "explanation": "No Boolean action assignment satisfies both manually normalized rules during the shared interval. This is a conditional compliance-feasibility result, not a legal ruling."}
    if result == sat:
        action = bool(solver.model().eval(perform, model_completion=True))
        return {**base, "verdict": "SATISFIABLE_UNDER_ENCODING", "solverStatus": "sat",
                "witness": {"performAct": action},
                "explanation": "At least one Boolean action assignment satisfies these two normalized rules. Other legal constraints may still apply."}
    return {**base, "verdict": "REVIEW_REQUIRED", "solverStatus": "unknown",
            "explanation": "The solver did not finish with a conclusive result; review the rules manually."}
