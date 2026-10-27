"""Adversarial checks for the bounded formal-feasibility claim."""

from fastapi.testclient import TestClient

from backend.main import app


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
