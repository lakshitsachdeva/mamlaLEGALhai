"""Adversarial checks for the bounded formal-feasibility claim."""

from fastapi.testclient import TestClient
from unittest.mock import patch

from backend.main import app
from backend.neural import NeuralUnavailable


client = TestClient(app)


def rule(rule_id: str, modality: str, **changes: str) -> dict:
    evidence = f"The records team {'must' if modality == 'OBLIGATION' else 'must not'} delete the test record."
    result = {
        "id": rule_id, "sourceId": f"fictional-{rule_id}", "sourceText": evidence,
        "evidence": evidence, "sourceSpan": {"start": 0, "end": len(evidence)},
        "actor": "records team", "action": "delete", "object": "test record",
        "scope": "review dataset", "jurisdiction": "fictional jurisdiction",
        "condition": "during review", "exception": "none",
        "validFrom": "2026-01-01", "validUntil": "2026-12-31", "modality": modality,
    }
    result.update(changes)
    return result


def check(left: dict, right: dict) -> dict:
    response = client.post("/api/contradictions/check", json={"left": left, "right": right})
    assert response.status_code == 200, response.json()
    return response.json()


def test_opposed_rules_produce_unsat_core() -> None:
    result = check(rule("A", "OBLIGATION"), rule("B", "PROHIBITION"))
    assert result["verdict"] == "INFEASIBLE_TO_SATISFY"
    assert result["solverStatus"] == "unsat"
    assert result["proofCore"] == ["A", "B"]
    assert result["sharedInterval"] == {"start": "2026-01-01", "end": "2026-12-31"}


def test_matching_obligations_have_a_witness() -> None:
    result = check(rule("A", "OBLIGATION"), rule("B", "OBLIGATION"))
    assert result["verdict"] == "SATISFIABLE_UNDER_ENCODING"
    assert result["witness"] == {"performAct": True}


def test_actor_mismatch_does_not_claim_a_conflict() -> None:
    result = check(rule("A", "OBLIGATION"), rule("B", "PROHIBITION", actor="security team"))
    assert result["verdict"] == "NOT_COMPARABLE"
    assert result["alignment"]["actor"] is False
    assert result["solverStatus"] == "not_run"


def test_disjoint_dates_are_not_compared() -> None:
    result = check(rule("A", "OBLIGATION", validUntil="2026-03-31"), rule("B", "PROHIBITION", validFrom="2026-04-01"))
    assert result["verdict"] == "NOT_COMPARABLE"
    assert result["sharedInterval"] is None


def test_exception_and_permission_route_to_review() -> None:
    assert check(rule("A", "OBLIGATION", exception="court order"), rule("B", "PROHIBITION"))["verdict"] == "REVIEW_REQUIRED"
    assert check(rule("A", "PERMISSION"), rule("B", "PROHIBITION"))["verdict"] == "REVIEW_REQUIRED"


def test_broken_evidence_offset_is_rejected() -> None:
    left = rule("A", "OBLIGATION")
    left["sourceSpan"]["end"] -= 1
    response = client.post("/api/contradictions/check", json={"left": left, "right": rule("B", "PROHIBITION")})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_unicode_prefix_uses_codepoint_offsets() -> None:
    left = rule("A", "OBLIGATION")
    left["sourceText"] = "🧭 Section 1. " + left["evidence"]
    left["sourceSpan"] = {"start": len("🧭 Section 1. "), "end": len(left["sourceText"])}
    assert check(left, rule("B", "PROHIBITION"))["solverStatus"] == "unsat"


def test_neural_signal_and_symbolic_proof_are_separate() -> None:
    signal = {
        "modelId": "law-ai/InLegalBERT", "modelRevision": "test-revision",
        "cosineSimilarity": 0.91, "method": "test embedding cosine",
        "truncated": {"left": False, "right": False},
        "note": "Uncalibrated relatedness signal, not a contradiction probability.",
    }
    left, right = rule("A", "OBLIGATION"), rule("B", "PROHIBITION")
    with patch("backend.main.score_evidence_pair", return_value=signal) as scorer:
        response = client.post("/api/contradictions/neuro-symbolic", json={
            "left": left, "right": right, "reviewConfirmed": True,
        })
    assert response.status_code == 200, response.json()
    assert response.json()["neural"]["cosineSimilarity"] == 0.91
    assert response.json()["symbolic"]["solverStatus"] == "unsat"
    assert response.json()["symbolic"]["proofCore"] == ["A", "B"]
    scorer.assert_called_once_with(left["evidence"], right["evidence"])


def test_neural_path_requires_review_confirmation() -> None:
    response = client.post("/api/contradictions/neuro-symbolic", json={
        "left": rule("A", "OBLIGATION"), "right": rule("B", "PROHIBITION"),
        "reviewConfirmed": False,
    })
    assert response.status_code == 422


def test_neural_path_reports_missing_model_without_symbolic_fallback() -> None:
    with patch("backend.main.score_evidence_pair", side_effect=NeuralUnavailable("Install optional model dependencies.")):
        response = client.post("/api/contradictions/neuro-symbolic", json={
            "left": rule("A", "OBLIGATION"), "right": rule("B", "PROHIBITION"),
            "reviewConfirmed": True,
        })
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "NEURAL_UNAVAILABLE"
